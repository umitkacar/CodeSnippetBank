"""
JSON Mode and Structured Outputs
Force LLMs to output valid JSON with schema validation.
"""

import json
from typing import Dict, Any, Optional, Type, List, Tuple
from dataclasses import dataclass, asdict, is_dataclass, fields
from enum import Enum

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


@dataclass
class JSONSchema:
    """JSON schema definition."""
    type: str
    properties: Dict[str, Any]
    required: List[str]
    description: Optional[str] = None


class JSONModePrompt:
    """Generate prompts for JSON output."""

    @staticmethod
    def create_json_prompt(
        task: str,
        schema: Dict[str, Any],
        example: Optional[Dict] = None
    ) -> str:
        """
        Create prompt that encourages JSON output.

        Args:
            task: Task description
            schema: JSON schema
            example: Optional example output

        Returns:
            Formatted prompt
        """
        prompt_parts = [
            task,
            "",
            "Output must be valid JSON matching this schema:",
            "```json",
            json.dumps(schema, indent=2),
            "```"
        ]

        if example:
            prompt_parts.extend([
                "",
                "Example output:",
                "```json",
                json.dumps(example, indent=2),
                "```"
            ])

        prompt_parts.extend([
            "",
            "Output only the JSON, no additional text.",
            "",
            "JSON:"
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def create_schema_from_dataclass(dataclass_type: Type) -> Dict[str, Any]:
        """
        Generate JSON schema from dataclass.

        Args:
            dataclass_type: Dataclass type

        Returns:
            JSON schema dictionary
        """
        if not is_dataclass(dataclass_type):
            raise ValueError("Type must be a dataclass")

        properties = {}
        required = []

        for field in fields(dataclass_type):
            field_type = field.type

            # Map Python types to JSON types
            json_type = "string"  # default

            if field_type == int:
                json_type = "integer"
            elif field_type == float:
                json_type = "number"
            elif field_type == bool:
                json_type = "boolean"
            elif field_type == list or hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                json_type = "array"
            elif field_type == dict or hasattr(field_type, '__origin__') and field_type.__origin__ == dict:
                json_type = "object"

            properties[field.name] = {
                "type": json_type
            }

            # Mark as required if no default value
            if field.default == field.default_factory == dataclasses.MISSING:
                required.append(field.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }


class JSONValidator:
    """Validate JSON outputs against schemas."""

    @staticmethod
    def validate(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON data against schema.

        Args:
            data: JSON data to validate
            schema: JSON schema

        Returns:
            Tuple of (is_valid, error_message)

        Raises:
            ImportError: If jsonschema not installed
        """
        if not JSONSCHEMA_AVAILABLE:
            raise ImportError("jsonschema not installed. Install with: pip install jsonschema")

        try:
            jsonschema.validate(instance=data, schema=schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)

    @staticmethod
    def fix_common_issues(json_str: str) -> str:
        """
        Fix common JSON formatting issues.

        Args:
            json_str: JSON string

        Returns:
            Fixed JSON string
        """
        # Remove markdown code blocks
        import re

        json_str = re.sub(r'```json\s*', '', json_str)
        json_str = re.sub(r'```\s*$', '', json_str)

        # Remove leading/trailing whitespace
        json_str = json_str.strip()

        # Fix single quotes to double quotes
        # (simple version - doesn't handle all cases)
        # json_str = json_str.replace("'", '"')

        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        return json_str


class StructuredOutputParser:
    """Parse LLM outputs into structured formats."""

    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize parser.

        Args:
            schema: JSON schema for output
        """
        self.schema = schema
        self.validator = JSONValidator()

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse text into structured format.

        Args:
            text: LLM output text

        Returns:
            Parsed dictionary

        Raises:
            ValueError: If parsing or validation fails
        """
        # Extract JSON from text
        json_str = self.validator.fix_common_issues(text)

        # Try to parse
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

        # Validate against schema
        is_valid, error = self.validator.validate(data, self.schema)

        if not is_valid:
            raise ValueError(f"Schema validation failed: {error}")

        return data

    def parse_with_retry(
        self,
        text: str,
        max_attempts: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Parse with retry on failure.

        Args:
            text: LLM output text
            max_attempts: Maximum retry attempts

        Returns:
            Parsed dictionary or None
        """
        for attempt in range(max_attempts):
            try:
                return self.parse(text)
            except ValueError as e:
                if attempt == max_attempts - 1:
                    return None

        return None


class TypedOutputParser:
    """Parse outputs into typed Python objects."""

    def __init__(self, output_type: Type):
        """
        Initialize typed parser.

        Args:
            output_type: Target type (dataclass)
        """
        if not is_dataclass(output_type):
            raise ValueError("Output type must be a dataclass")

        self.output_type = output_type
        self.schema = JSONModePrompt.create_schema_from_dataclass(output_type)
        self.parser = StructuredOutputParser(self.schema)

    def parse(self, text: str):
        """
        Parse text into typed object.

        Args:
            text: LLM output

        Returns:
            Instance of output_type
        """
        data = self.parser.parse(text)
        return self.output_type(**data)

    def get_prompt_template(self, task: str) -> str:
        """
        Get prompt template for this output type.

        Args:
            task: Task description

        Returns:
            Prompt string
        """
        return JSONModePrompt.create_json_prompt(task, self.schema)


import dataclasses

# Usage Examples
if __name__ == "__main__":
    # Example 1: Create JSON prompt
    print("=== JSON Mode Prompt ===")

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"}
        },
        "required": ["name", "age"]
    }

    prompt = JSONModePrompt.create_json_prompt(
        "Extract person information from this text: John Doe is 30 years old, email: john@example.com",
        schema=schema,
        example={"name": "Jane Smith", "age": 25, "email": "jane@example.com"}
    )

    print(prompt)
    print()

    # Example 2: Validate JSON
    print("=== JSON Validation ===")

    if JSONSCHEMA_AVAILABLE:
        validator = JSONValidator()

        valid_data = {"name": "John", "age": 30}
        invalid_data = {"name": "John"}  # missing required 'age'

        is_valid, error = validator.validate(valid_data, schema)
        print(f"Valid data: {is_valid}")

        is_valid, error = validator.validate(invalid_data, schema)
        print(f"Invalid data: {is_valid}, Error: {error}")
    else:
        print("jsonschema not installed. Skipping validation example.")
        print("Install with: pip install jsonschema")
    print()

    # Example 3: Parse structured output
    print("=== Structured Output Parser ===")

    if JSONSCHEMA_AVAILABLE:
        parser = StructuredOutputParser(schema)

        llm_output = """
        Here's the extracted information:
        ```json
        {
            "name": "Alice Johnson",
            "age": 28,
            "email": "alice@example.com"
        }
        ```
        """

        try:
            result = parser.parse(llm_output)
            print(f"Parsed result: {result}")
        except ValueError as e:
            print(f"Parse error: {e}")
    else:
        print("jsonschema not installed. Skipping parser example.")
    print()

    # Example 4: Typed output parser
    print("=== Typed Output Parser ===")

    if JSONSCHEMA_AVAILABLE:
        @dataclass
        class Person:
            name: str
            age: int
            email: str
            occupation: Optional[str] = None

        typed_parser = TypedOutputParser(Person)

        prompt = typed_parser.get_prompt_template(
            "Extract person information from: Dr. Sarah Wilson, 45, works as a surgeon, sarah.w@hospital.com"
        )

        print("Prompt template:")
        print(prompt[:200] + "...")
        print()

        # Simulate LLM response
        llm_response = """{
            "name": "Dr. Sarah Wilson",
            "age": 45,
            "email": "sarah.w@hospital.com",
            "occupation": "surgeon"
        }"""

        try:
            person = typed_parser.parse(llm_response)
            print(f"Parsed person: {person}")
            print(f"Type: {type(person)}")
        except Exception as e:
            print(f"Error parsing: {e}")
    else:
        print("jsonschema not installed. Skipping typed parser example.")
