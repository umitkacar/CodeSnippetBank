"""
Output Parsers
Parse and validate LLM outputs into structured formats.
"""

import re
import json
from typing import List, Dict, Any, Optional, Type, get_type_hints
from dataclasses import dataclass, is_dataclass, fields
from enum import Enum
import ast


class OutputParser:
    """Base class for output parsers."""

    def parse(self, text: str) -> Any:
        """Parse text into structured format."""
        raise NotImplementedError

    def get_format_instructions(self) -> str:
        """Get instructions for LLM on output format."""
        raise NotImplementedError


class JSONParser(OutputParser):
    """Parse JSON output from LLM."""

    def __init__(self, strict: bool = True):
        """
        Initialize JSON parser.

        Args:
            strict: Whether to use strict JSON parsing
        """
        self.strict = strict

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from text.

        Args:
            text: LLM output containing JSON

        Returns:
            Parsed dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        # Try to find JSON object in text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)

        try:
            return json.loads(text, strict=self.strict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")

    def get_format_instructions(self) -> str:
        """Get JSON format instructions."""
        return """Output your response as a JSON object. Use this format:
```json
{
  "key1": "value1",
  "key2": "value2"
}
```"""


class ListParser(OutputParser):
    """Parse list output from LLM."""

    def __init__(
        self,
        separator: str = "\n",
        numbered: bool = False,
        strip_markers: bool = True
    ):
        """
        Initialize list parser.

        Args:
            separator: Item separator
            numbered: Whether list is numbered
            strip_markers: Strip bullets/numbers
        """
        self.separator = separator
        self.numbered = numbered
        self.strip_markers = strip_markers

    def parse(self, text: str) -> List[str]:
        """
        Parse list from text.

        Args:
            text: LLM output containing list

        Returns:
            List of items
        """
        items = text.split(self.separator)
        parsed_items = []

        for item in items:
            item = item.strip()

            if not item:
                continue

            if self.strip_markers:
                # Remove bullets, numbers, etc.
                item = re.sub(r'^\s*[-*•]\s*', '', item)
                item = re.sub(r'^\s*\d+[\.)]\s*', '', item)

            parsed_items.append(item)

        return parsed_items

    def get_format_instructions(self) -> str:
        """Get list format instructions."""
        if self.numbered:
            return """Output your response as a numbered list:
1. First item
2. Second item
3. Third item"""
        else:
            return """Output your response as a bulleted list:
- First item
- Second item
- Third item"""


class DataclassParser(OutputParser):
    """Parse output into a dataclass."""

    def __init__(self, dataclass_type: Type):
        """
        Initialize dataclass parser.

        Args:
            dataclass_type: Dataclass type to parse into
        """
        if not is_dataclass(dataclass_type):
            raise ValueError("Type must be a dataclass")

        self.dataclass_type = dataclass_type

    def parse(self, text: str) -> Any:
        """
        Parse text into dataclass instance.

        Args:
            text: LLM output containing JSON

        Returns:
            Dataclass instance
        """
        # First parse as JSON
        json_parser = JSONParser()
        data = json_parser.parse(text)

        # Create dataclass instance
        try:
            return self.dataclass_type(**data)
        except TypeError as e:
            raise ValueError(f"Failed to create {self.dataclass_type.__name__}: {e}")

    def get_format_instructions(self) -> str:
        """Get dataclass format instructions."""
        field_info = []

        for field in fields(self.dataclass_type):
            field_type = field.type
            type_str = getattr(field_type, '__name__', str(field_type))

            field_info.append(f'  "{field.name}": <{type_str}>')

        fields_str = ",\n".join(field_info)

        return f"""Output your response as a JSON object matching this structure:
```json
{{
{fields_str}
}}
```"""


class EnumParser(OutputParser):
    """Parse output into enum value."""

    def __init__(self, enum_type: Type[Enum]):
        """
        Initialize enum parser.

        Args:
            enum_type: Enum type
        """
        self.enum_type = enum_type

    def parse(self, text: str) -> Enum:
        """
        Parse text into enum value.

        Args:
            text: LLM output

        Returns:
            Enum value
        """
        text = text.strip().upper()

        # Try exact match
        for enum_val in self.enum_type:
            if text == enum_val.name.upper():
                return enum_val

            if text == enum_val.value.upper():
                return enum_val

        # Try partial match
        for enum_val in self.enum_type:
            if enum_val.name.upper() in text or text in enum_val.name.upper():
                return enum_val

        raise ValueError(f"Could not parse '{text}' into {self.enum_type.__name__}")

    def get_format_instructions(self) -> str:
        """Get enum format instructions."""
        values = [f"- {e.value}" for e in self.enum_type]
        values_str = "\n".join(values)

        return f"""Output one of these values:
{values_str}"""


class RegexParser(OutputParser):
    """Parse output using regex patterns."""

    def __init__(
        self,
        pattern: str,
        group_names: Optional[List[str]] = None
    ):
        """
        Initialize regex parser.

        Args:
            pattern: Regex pattern
            group_names: Names for capture groups
        """
        self.pattern = re.compile(pattern, re.DOTALL)
        self.group_names = group_names

    def parse(self, text: str) -> Dict[str, str]:
        """
        Parse text using regex.

        Args:
            text: LLM output

        Returns:
            Dictionary of matched groups
        """
        match = self.pattern.search(text)

        if not match:
            raise ValueError(f"Pattern did not match text")

        if self.group_names:
            return {
                name: match.group(i + 1)
                for i, name in enumerate(self.group_names)
            }
        else:
            return match.groupdict()

    def get_format_instructions(self) -> str:
        """Get regex format instructions."""
        return f"Output must match pattern: {self.pattern.pattern}"


class XMLParser(OutputParser):
    """Parse XML-like structured output."""

    def parse(self, text: str) -> Dict[str, str]:
        """
        Parse XML-like tags.

        Args:
            text: LLM output with XML tags

        Returns:
            Dictionary of tag contents
        """
        result = {}

        # Find all tags
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            tag_name = match.group(1)
            content = match.group(2).strip()
            result[tag_name] = content

        return result

    def get_format_instructions(self) -> str:
        """Get XML format instructions."""
        return """Use XML-like tags for structure:
<tag1>Content 1</tag1>
<tag2>Content 2</tag2>"""


class CompositeParser(OutputParser):
    """Combine multiple parsers."""

    def __init__(self, parsers: List[OutputParser]):
        """
        Initialize composite parser.

        Args:
            parsers: List of parsers to try in order
        """
        self.parsers = parsers

    def parse(self, text: str) -> Any:
        """
        Try parsers in sequence until one succeeds.

        Args:
            text: LLM output

        Returns:
            Parsed output from first successful parser
        """
        errors = []

        for parser in self.parsers:
            try:
                return parser.parse(text)
            except Exception as e:
                errors.append(f"{parser.__class__.__name__}: {e}")

        raise ValueError(f"All parsers failed: {'; '.join(errors)}")

    def get_format_instructions(self) -> str:
        """Get combined format instructions."""
        instructions = ["You may use any of these formats:\n"]

        for i, parser in enumerate(self.parsers, 1):
            instructions.append(f"\nOption {i}:")
            instructions.append(parser.get_format_instructions())

        return "\n".join(instructions)


# Usage Examples
if __name__ == "__main__":
    # Example 1: JSON Parser
    print("=== JSON Parser ===")
    json_parser = JSONParser()

    json_text = '''
    Here's the information:
    ```json
    {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }
    ```
    '''

    result = json_parser.parse(json_text)
    print(f"Parsed: {result}")
    print(f"Instructions:\n{json_parser.get_format_instructions()}\n")

    # Example 2: List Parser
    print("=== List Parser ===")
    list_parser = ListParser(numbered=True)

    list_text = """
    Here are the items:
    1. First item
    2. Second item
    3. Third item
    """

    items = list_parser.parse(list_text)
    print(f"Parsed items: {items}\n")

    # Example 3: Dataclass Parser
    print("=== Dataclass Parser ===")

    @dataclass
    class Person:
        name: str
        age: int
        occupation: str

    dataclass_parser = DataclassParser(Person)

    person_text = '{"name": "Alice", "age": 25, "occupation": "Engineer"}'

    person = dataclass_parser.parse(person_text)
    print(f"Parsed person: {person}")
    print(f"Instructions:\n{dataclass_parser.get_format_instructions()}\n")

    # Example 4: Enum Parser
    print("=== Enum Parser ===")

    class Sentiment(Enum):
        POSITIVE = "positive"
        NEGATIVE = "negative"
        NEUTRAL = "neutral"

    enum_parser = EnumParser(Sentiment)

    sentiment_text = "The sentiment is: POSITIVE"

    sentiment = enum_parser.parse(sentiment_text)
    print(f"Parsed sentiment: {sentiment}")
    print(f"Instructions:\n{enum_parser.get_format_instructions()}\n")

    # Example 5: Regex Parser
    print("=== Regex Parser ===")
    regex_parser = RegexParser(
        r"Name: (\w+), Age: (\d+)",
        group_names=["name", "age"]
    )

    regex_text = "The person is Name: Bob, Age: 35"

    matches = regex_parser.parse(regex_text)
    print(f"Parsed matches: {matches}\n")

    # Example 6: XML Parser
    print("=== XML Parser ===")
    xml_parser = XMLParser()

    xml_text = """
    <title>My Title</title>
    <content>This is the content</content>
    <author>John Smith</author>
    """

    xml_result = xml_parser.parse(xml_text)
    print(f"Parsed XML: {xml_result}\n")

    # Example 7: Composite Parser
    print("=== Composite Parser ===")
    composite = CompositeParser([
        json_parser,
        xml_parser,
        list_parser
    ])

    # Will try JSON first, then XML, then list
    test_text = "<name>Test</name><value>123</value>"
    result = composite.parse(test_text)
    print(f"Composite parsed: {result}")
