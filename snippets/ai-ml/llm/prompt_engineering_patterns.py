"""
Prompt Engineering Patterns
Production-ready prompt templates and patterns for better LLM outputs.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PromptPattern(Enum):
    """Common prompt engineering patterns."""
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    REACT = "react"
    ROLE_PLAYING = "role_playing"
    STRUCTURED_OUTPUT = "structured_output"
    SELF_CONSISTENCY = "self_consistency"
    TREE_OF_THOUGHTS = "tree_of_thoughts"


@dataclass
class PromptTemplate:
    """Container for prompt templates."""
    name: str
    pattern: PromptPattern
    template: str
    variables: List[str]
    examples: Optional[List[str]] = None


class PromptBuilder:
    """Build optimized prompts using various patterns."""

    @staticmethod
    def zero_shot(
        task: str,
        context: Optional[str] = None,
        constraints: Optional[List[str]] = None
    ) -> str:
        """
        Zero-shot prompt without examples.

        Args:
            task: Task description
            context: Optional context
            constraints: Optional constraints

        Returns:
            Formatted prompt
        """
        prompt_parts = []

        if context:
            prompt_parts.append(f"Context: {context}\n")

        prompt_parts.append(f"Task: {task}\n")

        if constraints:
            prompt_parts.append("\nConstraints:")
            for constraint in constraints:
                prompt_parts.append(f"- {constraint}")
            prompt_parts.append("")

        return "\n".join(prompt_parts)

    @staticmethod
    def few_shot(
        task: str,
        examples: List[Dict[str, str]],
        query: str,
        context: Optional[str] = None
    ) -> str:
        """
        Few-shot prompt with examples.

        Args:
            task: Task description
            examples: List of input-output examples
            query: New query to process
            context: Optional context

        Returns:
            Formatted prompt
        """
        prompt_parts = []

        if context:
            prompt_parts.append(f"Context: {context}\n")

        prompt_parts.append(f"Task: {task}\n")
        prompt_parts.append("Examples:\n")

        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Input: {example['input']}")
            prompt_parts.append(f"Output: {example['output']}\n")

        prompt_parts.append(f"Now, process this input:")
        prompt_parts.append(f"Input: {query}")
        prompt_parts.append("Output:")

        return "\n".join(prompt_parts)

    @staticmethod
    def chain_of_thought(
        task: str,
        query: str,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Chain-of-thought prompt for step-by-step reasoning.

        Args:
            task: Task description
            query: Query to process
            examples: Optional examples with reasoning steps

        Returns:
            Formatted prompt
        """
        prompt_parts = [f"Task: {task}\n"]

        if examples:
            prompt_parts.append("Examples with reasoning:\n")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"Example {i}:")
                prompt_parts.append(f"Question: {example['question']}")
                prompt_parts.append(f"Reasoning: {example['reasoning']}")
                prompt_parts.append(f"Answer: {example['answer']}\n")

        prompt_parts.append(f"Now solve this:")
        prompt_parts.append(f"Question: {query}")
        prompt_parts.append("Let's think step by step:")

        return "\n".join(prompt_parts)

    @staticmethod
    def react_pattern(
        task: str,
        available_actions: List[str],
        query: str
    ) -> str:
        """
        ReAct pattern (Reasoning + Acting).

        Args:
            task: Task description
            available_actions: List of available actions
            query: Query to process

        Returns:
            Formatted prompt
        """
        actions_str = "\n".join(f"- {action}" for action in available_actions)

        prompt = f"""Task: {task}

Available Actions:
{actions_str}

For each step, follow this format:
Thought: [your reasoning about what to do next]
Action: [the action to take]
Observation: [what you observe from the action]

Continue until you can provide a final answer.

Question: {query}

Let's begin:
Thought:"""

        return prompt

    @staticmethod
    def role_playing(
        role: str,
        expertise: List[str],
        task: str,
        query: str,
        tone: Optional[str] = None
    ) -> str:
        """
        Role-playing prompt for specialized responses.

        Args:
            role: Role to play (e.g., "expert programmer")
            expertise: Areas of expertise
            task: Task to perform
            query: Query to process
            tone: Optional tone (professional, casual, etc.)

        Returns:
            Formatted prompt
        """
        expertise_str = ", ".join(expertise)

        prompt_parts = [
            f"You are a {role} with expertise in: {expertise_str}.",
        ]

        if tone:
            prompt_parts.append(f"Communicate in a {tone} tone.")

        prompt_parts.extend([
            f"\nTask: {task}",
            f"\nQuestion: {query}",
            "\nResponse:"
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def structured_output(
        task: str,
        query: str,
        output_format: Dict[str, str],
        example: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Prompt for structured/formatted output.

        Args:
            task: Task description
            query: Query to process
            output_format: Expected output structure
            example: Optional example output

        Returns:
            Formatted prompt
        """
        format_str = "\n".join(
            f"- {key}: {description}"
            for key, description in output_format.items()
        )

        prompt_parts = [
            f"Task: {task}",
            f"\nOutput Format:",
            format_str
        ]

        if example:
            prompt_parts.append("\nExample Output:")
            prompt_parts.append(str(example))

        prompt_parts.extend([
            f"\nInput: {query}",
            "\nOutput (follow the format exactly):"
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def self_consistency(
        task: str,
        query: str,
        num_samples: int = 3
    ) -> str:
        """
        Self-consistency prompt for multiple reasoning paths.

        Args:
            task: Task description
            query: Query to process
            num_samples: Number of reasoning paths to generate

        Returns:
            Formatted prompt
        """
        prompt = f"""Task: {task}

Question: {query}

Generate {num_samples} different reasoning paths to solve this problem.
For each path, show your step-by-step thinking.
Finally, determine the most consistent answer across all paths.

Reasoning Path 1:
"""
        return prompt

    @staticmethod
    def tree_of_thoughts(
        task: str,
        query: str,
        branching_factor: int = 3,
        depth: int = 2
    ) -> str:
        """
        Tree of thoughts prompt for exploring multiple solution paths.

        Args:
            task: Task description
            query: Query to process
            branching_factor: Number of branches per level
            depth: Tree depth

        Returns:
            Formatted prompt
        """
        prompt = f"""Task: {task}

Question: {query}

Explore {branching_factor} different approaches at each step for {depth} levels.
Evaluate each approach and choose the best path forward.

Level 1 - Generate {branching_factor} initial approaches:
Approach 1:"""

        return prompt


class PromptOptimizer:
    """Optimize prompts for better performance."""

    @staticmethod
    def add_clarity_markers(prompt: str) -> str:
        """Add markers to improve clarity."""
        return f"""<task>
{prompt}
</task>

Think carefully and provide a detailed response."""

    @staticmethod
    def add_constraints(
        prompt: str,
        max_length: Optional[int] = None,
        format_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """Add explicit constraints."""
        constraints = []

        if max_length:
            constraints.append(f"Maximum length: {max_length} words")
        if format_type:
            constraints.append(f"Format: {format_type}")
        if language:
            constraints.append(f"Language: {language}")

        if constraints:
            constraints_str = "\n".join(f"- {c}" for c in constraints)
            return f"{prompt}\n\nConstraints:\n{constraints_str}"

        return prompt

    @staticmethod
    def add_examples_separator(prompt: str) -> str:
        """Add clear separators for examples."""
        return prompt.replace("Examples:", "=== EXAMPLES ===\n").replace(
            "Now,", "\n=== YOUR TURN ===\nNow,"
        )

    @staticmethod
    def add_output_primer(prompt: str, primer: str = "Sure, here is") -> str:
        """Add output primer to guide response format."""
        return f"{prompt}\n\n{primer}"


# Usage Examples
if __name__ == "__main__":
    builder = PromptBuilder()

    # Zero-shot example
    print("=== Zero-Shot Prompt ===")
    zero_shot = builder.zero_shot(
        task="Classify the sentiment of the following text",
        context="Customer product review",
        constraints=["Output only: Positive, Negative, or Neutral"]
    )
    print(zero_shot)
    print()

    # Few-shot example
    print("=== Few-Shot Prompt ===")
    few_shot = builder.few_shot(
        task="Translate English to French",
        examples=[
            {"input": "Hello", "output": "Bonjour"},
            {"input": "Goodbye", "output": "Au revoir"},
            {"input": "Thank you", "output": "Merci"}
        ],
        query="Good morning"
    )
    print(few_shot)
    print()

    # Chain-of-thought example
    print("=== Chain-of-Thought Prompt ===")
    cot = builder.chain_of_thought(
        task="Solve math word problems",
        query="If a train travels 120 miles in 2 hours, how long will it take to travel 300 miles?",
        examples=[
            {
                "question": "A car travels 60 miles in 1 hour. How far in 3 hours?",
                "reasoning": "Speed = 60 miles/hour. In 3 hours: 60 * 3 = 180 miles",
                "answer": "180 miles"
            }
        ]
    )
    print(cot)
    print()

    # ReAct example
    print("=== ReAct Prompt ===")
    react = builder.react_pattern(
        task="Find information and answer questions",
        available_actions=["Search", "Lookup", "Calculate", "Finish"],
        query="What is the population of the capital of France?"
    )
    print(react)
    print()

    # Role-playing example
    print("=== Role-Playing Prompt ===")
    role = builder.role_playing(
        role="senior Python developer",
        expertise=["asyncio", "FastAPI", "pytest"],
        task="Review and improve code",
        query="How can I optimize this async function?",
        tone="professional"
    )
    print(role)
    print()

    # Structured output example
    print("=== Structured Output Prompt ===")
    structured = builder.structured_output(
        task="Extract information from text",
        query="John Doe, age 30, lives in New York, works as a software engineer",
        output_format={
            "name": "Full name",
            "age": "Age in years",
            "location": "City of residence",
            "occupation": "Job title"
        },
        example={
            "name": "Jane Smith",
            "age": 25,
            "location": "Los Angeles",
            "occupation": "Data Scientist"
        }
    )
    print(structured)
    print()

    # Optimize prompts
    optimizer = PromptOptimizer()

    optimized = optimizer.add_clarity_markers(
        optimizer.add_constraints(
            "Summarize this article",
            max_length=100,
            format_type="bullet points"
        )
    )
    print("=== Optimized Prompt ===")
    print(optimized)
