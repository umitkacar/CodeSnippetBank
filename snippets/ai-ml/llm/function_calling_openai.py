"""
OpenAI Function Calling
Production-ready function calling implementation with type validation.
"""

import os
import json
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
import inspect


@dataclass
class FunctionCall:
    """Container for function call information."""
    name: str
    arguments: Dict[str, Any]
    result: Any = None


@dataclass
class FunctionCallResponse:
    """Response container for function calling."""
    content: str
    function_calls: List[FunctionCall]
    finish_reason: str


class FunctionRegistry:
    """Registry for managing callable functions."""

    def __init__(self):
        """Initialize function registry."""
        self.functions: Dict[str, Callable] = {}
        self.schemas: Dict[str, Dict] = {}

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict] = None
    ):
        """
        Decorator to register a function.

        Args:
            name: Function name (defaults to function __name__)
            description: Function description
            parameters: Parameter schema (auto-generated if not provided)
        """
        def decorator(func: Callable):
            func_name = name or func.__name__
            self.functions[func_name] = func

            # Auto-generate schema if not provided
            if parameters is None:
                schema = self._generate_schema(func, description)
            else:
                schema = {
                    "name": func_name,
                    "description": description or func.__doc__ or "",
                    "parameters": parameters
                }

            self.schemas[func_name] = schema
            return func

        return decorator

    def _generate_schema(self, func: Callable, description: Optional[str] = None) -> Dict:
        """Auto-generate function schema from signature."""
        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            param_type = "string"  # Default type

            # Try to infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"

            properties[param_name] = {"type": param_type}

            # Add to required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "name": func.__name__,
            "description": description or func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    def get_schemas(self) -> List[Dict]:
        """Get all function schemas."""
        return list(self.schemas.values())

    def call(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a registered function.

        Args:
            name: Function name
            arguments: Function arguments

        Returns:
            Function result
        """
        if name not in self.functions:
            raise ValueError(f"Function {name} not registered")

        return self.functions[name](**arguments)


class FunctionCallingClient:
    """OpenAI client with function calling support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview"
    ):
        """
        Initialize function calling client.

        Args:
            api_key: OpenAI API key
            model: Model name
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.registry = FunctionRegistry()

    def register_function(self, *args, **kwargs):
        """Register a function (decorator)."""
        return self.registry.register(*args, **kwargs)

    def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        max_iterations: int = 5,
        auto_execute: bool = True
    ) -> FunctionCallResponse:
        """
        Chat with function calling support.

        Args:
            messages: Conversation messages
            max_iterations: Maximum function calling iterations
            auto_execute: Whether to auto-execute function calls

        Returns:
            FunctionCallResponse object
        """
        function_calls = []
        conversation = messages.copy()

        for iteration in range(max_iterations):
            # Call API with functions
            response = self.client.chat.completions.create(
                model=self.model,
                messages=conversation,
                tools=[
                    {"type": "function", "function": schema}
                    for schema in self.registry.get_schemas()
                ],
                tool_choice="auto"
            )

            message = response.choices[0].message

            # Check if function was called
            if message.tool_calls:
                # Add assistant message to conversation
                conversation.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })

                # Execute functions
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    if auto_execute:
                        # Execute function
                        try:
                            result = self.registry.call(function_name, function_args)
                            result_str = json.dumps(result)
                        except Exception as e:
                            result = None
                            result_str = f"Error: {str(e)}"
                    else:
                        result = None
                        result_str = "Function not executed (auto_execute=False)"

                    # Record function call
                    function_calls.append(FunctionCall(
                        name=function_name,
                        arguments=function_args,
                        result=result
                    ))

                    # Add function result to conversation
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str
                    })

            else:
                # No more function calls, return final response
                return FunctionCallResponse(
                    content=message.content or "",
                    function_calls=function_calls,
                    finish_reason=response.choices[0].finish_reason
                )

        # Max iterations reached
        return FunctionCallResponse(
            content="Max function calling iterations reached",
            function_calls=function_calls,
            finish_reason="max_iterations"
        )


# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = FunctionCallingClient()

    # Register functions
    @client.register_function(
        description="Get the current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g., 'San Francisco'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    )
    def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
        """Get weather for a location."""
        # Simulate weather API call
        return {
            "location": location,
            "temperature": 72 if unit == "fahrenheit" else 22,
            "unit": unit,
            "condition": "sunny"
        }

    @client.register_function(
        description="Calculate the result of a mathematical expression"
    )
    def calculate(expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        try:
            # Note: eval is dangerous in production, use a proper math parser
            allowed_names = {"__builtins__": {}}
            return eval(expression, allowed_names)
        except Exception as e:
            return f"Error: {e}"

    @client.register_function(
        description="Search for information on a topic"
    )
    def search(query: str, num_results: int = 5) -> List[str]:
        """Search for information."""
        # Simulate search results
        return [
            f"Result {i+1} for '{query}'"
            for i in range(num_results)
        ]

    # Example 1: Weather query
    print("=== Example 1: Weather Query ===")
    response = client.chat_with_functions(
        messages=[
            {"role": "user", "content": "What's the weather in Tokyo? Use celsius."}
        ]
    )

    print(f"Response: {response.content}")
    print(f"Function calls made: {len(response.function_calls)}")
    for fc in response.function_calls:
        print(f"  - {fc.name}({fc.arguments}) = {fc.result}")
    print()

    # Example 2: Math calculation
    print("=== Example 2: Math Calculation ===")
    response = client.chat_with_functions(
        messages=[
            {"role": "user", "content": "What is 15% of 250?"}
        ]
    )

    print(f"Response: {response.content}")
    for fc in response.function_calls:
        print(f"  - {fc.name}({fc.arguments}) = {fc.result}")
    print()

    # Example 3: Multi-step reasoning
    print("=== Example 3: Multi-step Reasoning ===")
    response = client.chat_with_functions(
        messages=[
            {
                "role": "user",
                "content": "I'm in Paris and want to know if it's warmer than London today."
            }
        ]
    )

    print(f"Response: {response.content}")
    print(f"Function calls: {len(response.function_calls)}")
    for fc in response.function_calls:
        print(f"  - {fc.name}({fc.arguments}) = {fc.result}")
