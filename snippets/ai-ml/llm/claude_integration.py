"""
Claude API Integration
Production-ready Anthropic Claude client with advanced features.
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import time

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    # Fallback decorator if tenacity not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def stop_after_attempt(n):
        return None
    def wait_exponential(**kwargs):
        return None


@dataclass
class ClaudeResponse:
    """Response container for Claude completions."""
    content: str
    model: str
    stop_reason: str
    tokens_used: int
    response_time: float


class ClaudeClient:
    """Production-ready Claude client with retry logic."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 4000,
        temperature: float = 1.0
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name (claude-3-opus, claude-3-sonnet, claude-3-haiku)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 1.0)

        Raises:
            ImportError: If anthropic package not installed
            ValueError: If API key not provided
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic not installed. Install with: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> ClaudeResponse:
        """
        Generate completion with Claude.

        Args:
            prompt: User prompt
            system: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            ClaudeResponse object

        Raises:
            anthropic.APIError: On API errors after retries
        """
        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system or "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_time = time.time() - start_time

            return ClaudeResponse(
                content=response.content[0].text,
                model=response.model,
                stop_reason=response.stop_reason,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                response_time=response_time
            )

        except Exception as e:
            print(f"Claude API error: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        **kwargs
    ) -> ClaudeResponse:
        """
        Multi-turn conversation with Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            ClaudeResponse object
        """
        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system or "",
                messages=messages
            )

            response_time = time.time() - start_time

            return ClaudeResponse(
                content=response.content[0].text,
                model=response.model,
                stop_reason=response.stop_reason,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                response_time=response_time
            )

        except Exception as e:
            print(f"Claude chat error: {e}")
            raise

    def stream_complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ):
        """
        Stream completion tokens from Claude.

        Args:
            prompt: User prompt
            system: Optional system prompt
            **kwargs: Additional parameters

        Yields:
            Text chunks as they arrive
        """
        try:
            with self.client.messages.stream(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                messages=[{"role": "user", "content": prompt}],
                system=system or ""
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            print(f"Claude streaming error: {e}")
            raise


class ClaudeChatSession:
    """Maintain a conversation session with Claude."""

    def __init__(
        self,
        client: ClaudeClient,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize chat session.

        Args:
            client: ClaudeClient instance
            system_prompt: Optional system prompt
        """
        self.client = client
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")

        self.messages.append({"role": role, "content": content})

    def send(self, user_message: str) -> ClaudeResponse:
        """
        Send a message and get response.

        Args:
            user_message: User's message

        Returns:
            ClaudeResponse object
        """
        self.add_message("user", user_message)

        response = self.client.chat(
            messages=self.messages,
            system=self.system_prompt
        )

        self.add_message("assistant", response.content)

        return response

    def clear_history(self):
        """Clear conversation history."""
        self.messages = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.messages.copy()


class ClaudeToolsClient:
    """Claude with tool/function calling support."""

    def __init__(self, client: ClaudeClient):
        """Initialize with Claude client."""
        self.client = client

    def complete_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system: Optional[str] = None
    ) -> ClaudeResponse:
        """
        Complete with tool definitions.

        Args:
            prompt: User prompt
            tools: List of tool definitions
            system: Optional system prompt

        Returns:
            ClaudeResponse object
        """
        try:
            response = self.client.client.messages.create(
                model=self.client.model,
                max_tokens=self.client.max_tokens,
                tools=tools,
                messages=[{"role": "user", "content": prompt}],
                system=system or ""
            )

            return ClaudeResponse(
                content=str(response.content),
                model=response.model,
                stop_reason=response.stop_reason,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                response_time=0.0
            )

        except Exception as e:
            print(f"Tool calling error: {e}")
            raise


# Usage Examples
if __name__ == "__main__":
    if not ANTHROPIC_AVAILABLE:
        print("Error: anthropic package not installed")
        print("Install with: pip install anthropic")
        exit(1)

    try:
        # Initialize client
        client = ClaudeClient(
            model="claude-3-sonnet-20240229",
            max_tokens=2000
        )
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)

    # Single completion
    response = client.complete(
        prompt="Explain the difference between lists and tuples in Python.",
        system="You are an expert Python developer."
    )

    print(f"Response: {response.content[:200]}...")
    print(f"Tokens: {response.tokens_used}")
    print(f"Time: {response.response_time:.2f}s\n")

    # Chat session
    session = ClaudeChatSession(
        client,
        system_prompt="You are a helpful coding assistant."
    )

    response1 = session.send("What is recursion?")
    print(f"Response 1: {response1.content[:150]}...\n")

    response2 = session.send("Give me a Python example.")
    print(f"Response 2: {response2.content[:150]}...\n")

    # Streaming
    print("Streaming response:")
    for chunk in client.stream_complete(
        "Write a short poem about AI.",
        system="You are a creative poet."
    ):
        print(chunk, end="", flush=True)
    print("\n")

    # Tool example
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    ]

    tools_client = ClaudeToolsClient(client)
    tool_response = tools_client.complete_with_tools(
        "What's the weather in San Francisco?",
        tools=tools
    )
    print(f"Tool response: {tool_response.content}")
