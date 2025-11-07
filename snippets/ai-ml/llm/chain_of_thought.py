"""
Chain-of-Thought Reasoning
Implementation of CoT, Self-Consistency, and Tree-of-Thoughts patterns.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import re


@dataclass
class ReasoningStep:
    """Container for a single reasoning step."""
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None


@dataclass
class CoTResponse:
    """Container for chain-of-thought response."""
    question: str
    reasoning_steps: List[ReasoningStep]
    final_answer: str
    confidence: Optional[float] = None


class ChainOfThoughtPrompt:
    """Generate chain-of-thought prompts."""

    @staticmethod
    def zero_shot_cot(question: str) -> str:
        """
        Zero-shot chain-of-thought prompt.

        Args:
            question: Question to answer

        Returns:
            Formatted prompt with CoT instruction
        """
        return f"""{question}

Let's think step by step:"""

    @staticmethod
    def few_shot_cot(
        question: str,
        examples: List[Dict[str, Any]]
    ) -> str:
        """
        Few-shot chain-of-thought prompt.

        Args:
            question: Question to answer
            examples: List of example dicts with 'question', 'reasoning', 'answer'

        Returns:
            Formatted prompt with examples
        """
        parts = []

        for i, example in enumerate(examples, 1):
            parts.append(f"Question {i}: {example['question']}")
            parts.append(f"Let's think step by step:")
            parts.append(example['reasoning'])
            parts.append(f"Therefore, the answer is: {example['answer']}")
            parts.append("")

        parts.append(f"Question: {question}")
        parts.append("Let's think step by step:")

        return "\n".join(parts)

    @staticmethod
    def structured_cot(
        question: str,
        steps: List[str]
    ) -> str:
        """
        Structured CoT with predefined steps.

        Args:
            question: Question to answer
            steps: List of step descriptions

        Returns:
            Formatted prompt
        """
        parts = [f"Question: {question}", ""]

        for i, step in enumerate(steps, 1):
            parts.append(f"Step {i}: {step}")

        parts.append("")
        parts.append("Let's solve this step by step:")

        return "\n".join(parts)

    @staticmethod
    def least_to_most(
        question: str,
        decomposition_prompt: Optional[str] = None
    ) -> str:
        """
        Least-to-most prompting (decompose then solve).

        Args:
            question: Complex question
            decomposition_prompt: Custom decomposition instruction

        Returns:
            Formatted prompt
        """
        default_decomp = "Let's break this down into simpler sub-problems:"

        prompt = f"""{question}

{decomposition_prompt or default_decomp}

1."""

        return prompt


class SelfConsistency:
    """Self-consistency through multiple reasoning paths."""

    def __init__(self, num_samples: int = 5):
        """
        Initialize self-consistency.

        Args:
            num_samples: Number of reasoning paths to generate
        """
        self.num_samples = num_samples

    def create_prompt(self, question: str) -> List[str]:
        """
        Create multiple prompts for sampling.

        Args:
            question: Question to answer

        Returns:
            List of prompts (same prompt repeated for sampling)
        """
        base_prompt = f"""{question}

Let's approach this step by step:"""

        return [base_prompt] * self.num_samples

    def aggregate_answers(
        self,
        responses: List[str],
        extract_answer_fn: Optional[callable] = None
    ) -> Tuple[str, float]:
        """
        Aggregate multiple responses to find consensus.

        Args:
            responses: List of response strings
            extract_answer_fn: Function to extract final answer from response

        Returns:
            Tuple of (consensus_answer, confidence)
        """
        if extract_answer_fn is None:
            # Default: extract text after "answer is" or "answer:"
            extract_answer_fn = self._default_extract_answer

        # Extract answers
        answers = [extract_answer_fn(resp) for resp in responses]

        # Find most common answer
        answer_counts = Counter(answers)
        most_common_answer, count = answer_counts.most_common(1)[0]

        confidence = count / len(answers)

        return most_common_answer, confidence

    def _default_extract_answer(self, response: str) -> str:
        """Default answer extraction."""
        # Try to find answer after common patterns
        patterns = [
            r"(?:the )?answer is:?\s*(.+?)(?:\.|$)",
            r"(?:therefore|thus|hence),?\s*(?:the answer is)?\s*(.+?)(?:\.|$)",
            r"final answer:?\s*(.+?)(?:\.|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, response.lower(), re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback: last sentence
        sentences = response.split('.')
        return sentences[-1].strip() if sentences else response


class TreeOfThoughts:
    """Tree-of-Thoughts deliberate problem solving."""

    @dataclass
    class ThoughtNode:
        """Node in the thought tree."""
        thought: str
        level: int
        score: Optional[float] = None
        children: List['TreeOfThoughts.ThoughtNode'] = None

        def __post_init__(self):
            if self.children is None:
                self.children = []

    def create_expansion_prompt(
        self,
        question: str,
        current_path: List[str],
        num_branches: int = 3
    ) -> str:
        """
        Create prompt for expanding thought tree.

        Args:
            question: Original question
            current_path: Current reasoning path
            num_branches: Number of new thoughts to generate

        Returns:
            Formatted prompt
        """
        parts = [f"Question: {question}"]

        if current_path:
            parts.append("\nCurrent reasoning path:")
            for i, thought in enumerate(current_path, 1):
                parts.append(f"{i}. {thought}")

        parts.append(f"\nGenerate {num_branches} different next steps or approaches:")

        for i in range(num_branches):
            parts.append(f"{i+1}.")

        return "\n".join(parts)

    def create_evaluation_prompt(
        self,
        question: str,
        thought_path: List[str]
    ) -> str:
        """
        Create prompt for evaluating a thought path.

        Args:
            question: Original question
            thought_path: Reasoning path to evaluate

        Returns:
            Formatted prompt
        """
        path_str = "\n".join(
            f"{i}. {thought}"
            for i, thought in enumerate(thought_path, 1)
        )

        return f"""Question: {question}

Reasoning path:
{path_str}

Rate this reasoning path from 0 to 1, where:
- 0 = Completely wrong or unhelpful
- 0.5 = Partially correct but incomplete
- 1 = Correct and promising

Score:"""


class ReActPattern:
    """ReAct (Reasoning + Acting) pattern."""

    def create_prompt(
        self,
        question: str,
        available_actions: List[str],
        max_steps: int = 5
    ) -> str:
        """
        Create ReAct pattern prompt.

        Args:
            question: Question to answer
            available_actions: List of available actions
            max_steps: Maximum reasoning steps

        Returns:
            Formatted prompt
        """
        actions_str = "\n".join(f"- {action}" for action in available_actions)

        prompt = f"""Question: {question}

Available Actions:
{actions_str}

Solve this by alternating between Thought, Action, and Observation.

Format:
Thought 1: [Your reasoning about what to do]
Action 1: [Action to take]
Observation 1: [Result of the action]
Thought 2: [Reasoning based on observation]
...
Final Answer: [Your conclusion]

Begin:

Thought 1:"""

        return prompt

    def parse_react_response(self, response: str) -> List[Dict[str, str]]:
        """
        Parse ReAct response into structured steps.

        Args:
            response: ReAct formatted response

        Returns:
            List of step dictionaries
        """
        steps = []

        # Extract thought-action-observation triplets
        thought_pattern = r"Thought \d+:\s*(.+?)(?=Action \d+:|$)"
        action_pattern = r"Action \d+:\s*(.+?)(?=Observation \d+:|$)"
        observation_pattern = r"Observation \d+:\s*(.+?)(?=Thought \d+:|Final Answer:|$)"

        thoughts = re.findall(thought_pattern, response, re.DOTALL)
        actions = re.findall(action_pattern, response, re.DOTALL)
        observations = re.findall(observation_pattern, response, re.DOTALL)

        for i, (thought, action, observation) in enumerate(
            zip(thoughts, actions, observations), 1
        ):
            steps.append({
                "step": i,
                "thought": thought.strip(),
                "action": action.strip(),
                "observation": observation.strip()
            })

        # Extract final answer
        final_answer_match = re.search(
            r"Final Answer:\s*(.+)",
            response,
            re.DOTALL
        )

        if final_answer_match:
            steps.append({
                "step": len(steps) + 1,
                "type": "final_answer",
                "content": final_answer_match.group(1).strip()
            })

        return steps


class CoTAnalyzer:
    """Analyze chain-of-thought responses."""

    @staticmethod
    def count_reasoning_steps(response: str) -> int:
        """Count explicit reasoning steps in response."""
        # Count numbered steps
        numbered_steps = re.findall(r'^\s*\d+[\.)]\s', response, re.MULTILINE)

        # Count "first/second/third" patterns
        ordinal_steps = re.findall(
            r'\b(first|second|third|fourth|fifth|then|next|finally)\b',
            response.lower()
        )

        return max(len(numbered_steps), len(ordinal_steps))

    @staticmethod
    def extract_intermediate_conclusions(response: str) -> List[str]:
        """Extract intermediate conclusions."""
        patterns = [
            r"(?:therefore|thus|hence|so),?\s+(.+?)(?:\.|;|$)",
            r"(?:this means|this implies)\s+(.+?)(?:\.|;|$)",
        ]

        conclusions = []

        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            conclusions.extend(matches)

        return [c.strip() for c in conclusions]

    @staticmethod
    def has_backward_chaining(response: str) -> bool:
        """Check if response uses backward chaining."""
        indicators = [
            "working backwards",
            "start from the end",
            "reverse order",
            "from the goal"
        ]

        return any(ind in response.lower() for ind in indicators)


# Usage Examples
if __name__ == "__main__":
    # Example 1: Zero-shot CoT
    print("=== Zero-Shot CoT ===")
    cot = ChainOfThoughtPrompt()

    prompt = cot.zero_shot_cot(
        "If a train travels 120 miles in 2 hours, how long will it take to travel 300 miles?"
    )
    print(prompt)
    print()

    # Example 2: Few-shot CoT
    print("=== Few-Shot CoT ===")
    examples = [
        {
            "question": "If 5 apples cost $2, how much do 15 apples cost?",
            "reasoning": "First, find cost per apple: $2 / 5 = $0.40 per apple.\nThen, multiply by 15: $0.40 × 15 = $6.",
            "answer": "$6"
        }
    ]

    prompt2 = cot.few_shot_cot(
        "If 3 books cost $24, how much do 7 books cost?",
        examples
    )
    print(prompt2)
    print()

    # Example 3: Self-Consistency
    print("=== Self-Consistency ===")
    sc = SelfConsistency(num_samples=3)

    prompts = sc.create_prompt("What is 15% of 80?")
    print(f"Generated {len(prompts)} prompts for sampling\n")

    # Simulate responses
    sample_responses = [
        "Let's calculate: 15% = 0.15. So 0.15 × 80 = 12. The answer is 12.",
        "First, convert percentage: 15/100 = 0.15. Then multiply: 0.15 × 80 = 12. Therefore, the answer is 12.",
        "15% of 80 means (15/100) × 80 = 1200/100 = 12. The answer is 12."
    ]

    answer, confidence = sc.aggregate_answers(sample_responses)
    print(f"Consensus answer: {answer}")
    print(f"Confidence: {confidence:.2%}\n")

    # Example 4: ReAct
    print("=== ReAct Pattern ===")
    react = ReActPattern()

    react_prompt = react.create_prompt(
        "What is the population of the capital of France?",
        available_actions=["Search", "Lookup", "Calculate", "Finish"]
    )
    print(react_prompt)
    print()

    # Example 5: Tree of Thoughts
    print("=== Tree of Thoughts ===")
    tot = TreeOfThoughts()

    tot_prompt = tot.create_expansion_prompt(
        "How can I optimize a Python function that processes large CSV files?",
        current_path=["Consider memory usage optimization"],
        num_branches=3
    )
    print(tot_prompt)
