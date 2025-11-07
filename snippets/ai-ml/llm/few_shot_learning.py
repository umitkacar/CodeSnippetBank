"""
Few-Shot Learning Patterns
Dynamic few-shot example selection and formatting for LLMs.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import random
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


@dataclass
class Example:
    """Container for few-shot examples."""
    input: str
    output: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FewShotPrompt:
    """Container for formatted few-shot prompt."""
    prompt: str
    examples_used: List[Example]
    example_count: int


class ExampleSelector:
    """Select relevant examples for few-shot prompting."""

    def __init__(self, examples: List[Example]):
        """
        Initialize example selector.

        Args:
            examples: Pool of available examples
        """
        self.examples = examples

    def select_random(self, k: int = 3) -> List[Example]:
        """
        Randomly select k examples.

        Args:
            k: Number of examples to select

        Returns:
            List of selected examples
        """
        k = min(k, len(self.examples))
        return random.sample(self.examples, k)

    def select_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        k: int = 3
    ) -> List[Example]:
        """
        Select examples matching metadata criteria.

        Args:
            metadata_filter: Metadata key-value pairs to match
            k: Maximum examples to return

        Returns:
            List of matching examples
        """
        matching = []

        for example in self.examples:
            if not example.metadata:
                continue

            matches = all(
                example.metadata.get(key) == value
                for key, value in metadata_filter.items()
            )

            if matches:
                matching.append(example)

                if len(matching) >= k:
                    break

        return matching

    def select_diverse(self, k: int = 3) -> List[Example]:
        """
        Select diverse examples (simple heuristic).

        Args:
            k: Number of examples to select

        Returns:
            List of diverse examples
        """
        if len(self.examples) <= k:
            return self.examples

        # Simple diversity: maximize distance between examples
        selected = [self.examples[0]]

        for _ in range(k - 1):
            # Find example most different from selected
            max_distance = -1
            best_example = None

            for candidate in self.examples:
                if candidate in selected:
                    continue

                # Simple distance: token overlap
                min_similarity = min(
                    self._token_overlap(candidate.input, sel.input)
                    for sel in selected
                )

                if min_similarity < 0.5 and -min_similarity > max_distance:
                    max_distance = -min_similarity
                    best_example = candidate

            if best_example:
                selected.append(best_example)
            else:
                # Fallback: add any remaining example
                remaining = [ex for ex in self.examples if ex not in selected]
                if remaining:
                    selected.append(remaining[0])

        return selected[:k]

    def _token_overlap(self, text1: str, text2: str) -> float:
        """Calculate token overlap between two texts."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        return len(intersection) / len(union) if union else 0.0


class SemanticExampleSelector(ExampleSelector):
    """Select examples based on semantic similarity."""

    def __init__(
        self,
        examples: List[Example],
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize semantic selector.

        Args:
            examples: Pool of examples
            model_name: Sentence transformer model

        Raises:
            ImportError: If sentence-transformers not installed
        """
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")

        super().__init__(examples)

        self.model = SentenceTransformer(model_name)

        # Pre-compute embeddings
        self.embeddings = self.model.encode(
            [ex.input for ex in examples],
            convert_to_numpy=True
        )

    def select_similar(
        self,
        query: str,
        k: int = 3,
        diversity_penalty: float = 0.0
    ) -> List[Example]:
        """
        Select examples most similar to query.

        Args:
            query: Query text
            k: Number of examples to select
            diversity_penalty: Penalty for similar examples (0.0 to 1.0)

        Returns:
            List of similar examples
        """
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding)

        if diversity_penalty > 0:
            # Maximal Marginal Relevance
            selected_indices = []
            remaining_indices = list(range(len(self.examples)))

            for _ in range(min(k, len(self.examples))):
                if not remaining_indices:
                    break

                if not selected_indices:
                    # First selection: most similar
                    best_idx = remaining_indices[np.argmax(similarities[remaining_indices])]
                else:
                    # Balance similarity and diversity
                    scores = []

                    for idx in remaining_indices:
                        # Similarity to query
                        relevance = similarities[idx]

                        # Maximum similarity to already selected
                        selected_sims = [
                            np.dot(self.embeddings[idx], self.embeddings[sel_idx])
                            for sel_idx in selected_indices
                        ]
                        max_sim = max(selected_sims) if selected_sims else 0

                        # MMR score
                        score = relevance - diversity_penalty * max_sim
                        scores.append(score)

                    best_idx = remaining_indices[np.argmax(scores)]

                selected_indices.append(best_idx)
                remaining_indices.remove(best_idx)

            return [self.examples[i] for i in selected_indices]

        else:
            # Simple: top-k most similar
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            return [self.examples[i] for i in top_k_indices]


class FewShotFormatter:
    """Format few-shot prompts."""

    @staticmethod
    def format_basic(
        examples: List[Example],
        query: str,
        instruction: Optional[str] = None,
        input_label: str = "Input",
        output_label: str = "Output"
    ) -> str:
        """
        Basic few-shot formatting.

        Args:
            examples: List of examples
            query: New query to process
            instruction: Optional instruction
            input_label: Label for input
            output_label: Label for output

        Returns:
            Formatted prompt
        """
        parts = []

        if instruction:
            parts.append(instruction)
            parts.append("")

        # Add examples
        for i, example in enumerate(examples, 1):
            parts.append(f"Example {i}:")
            parts.append(f"{input_label}: {example.input}")
            parts.append(f"{output_label}: {example.output}")
            parts.append("")

        # Add query
        parts.append(f"Now process this:")
        parts.append(f"{input_label}: {query}")
        parts.append(f"{output_label}:")

        return "\n".join(parts)

    @staticmethod
    def format_conversational(
        examples: List[Example],
        query: str
    ) -> List[Dict[str, str]]:
        """
        Format as conversation messages.

        Args:
            examples: List of examples
            query: New query

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add examples as user-assistant pairs
        for example in examples:
            messages.append({
                "role": "user",
                "content": example.input
            })
            messages.append({
                "role": "assistant",
                "content": example.output
            })

        # Add new query
        messages.append({
            "role": "user",
            "content": query
        })

        return messages

    @staticmethod
    def format_with_reasoning(
        examples: List[Example],
        query: str,
        reasoning_key: str = "reasoning"
    ) -> str:
        """
        Format with reasoning steps (if available in metadata).

        Args:
            examples: List of examples
            query: New query
            reasoning_key: Metadata key for reasoning

        Returns:
            Formatted prompt
        """
        parts = []

        for i, example in enumerate(examples, 1):
            parts.append(f"Example {i}:")
            parts.append(f"Question: {example.input}")

            # Add reasoning if available
            if example.metadata and reasoning_key in example.metadata:
                parts.append(f"Reasoning: {example.metadata[reasoning_key]}")

            parts.append(f"Answer: {example.output}")
            parts.append("")

        parts.append(f"Now solve this:")
        parts.append(f"Question: {query}")
        parts.append(f"Reasoning:")

        return "\n".join(parts)


class DynamicFewShotPrompt:
    """Dynamically create few-shot prompts."""

    def __init__(
        self,
        examples: List[Example],
        selector_type: str = "semantic",
        formatter_type: str = "basic"
    ):
        """
        Initialize dynamic few-shot prompt generator.

        Args:
            examples: Pool of examples
            selector_type: "random", "semantic", or "diverse"
            formatter_type: "basic", "conversational", or "reasoning"
        """
        self.examples = examples

        # Initialize selector
        if selector_type == "semantic":
            if not EMBEDDINGS_AVAILABLE:
                print("Warning: sentence-transformers not available, using random selection")
                self.selector = ExampleSelector(examples)
                self.selector_type = "random"
            else:
                self.selector = SemanticExampleSelector(examples)
                self.selector_type = "semantic"
        else:
            self.selector = ExampleSelector(examples)
            self.selector_type = selector_type

        self.formatter = FewShotFormatter()
        self.formatter_type = formatter_type

    def create_prompt(
        self,
        query: str,
        k: int = 3,
        instruction: Optional[str] = None,
        **kwargs
    ) -> FewShotPrompt:
        """
        Create few-shot prompt for query.

        Args:
            query: Query to process
            k: Number of examples to include
            instruction: Optional instruction
            **kwargs: Additional formatting arguments

        Returns:
            FewShotPrompt object
        """
        # Select examples
        if self.selector_type == "semantic":
            selected = self.selector.select_similar(query, k=k)
        elif self.selector_type == "diverse":
            selected = self.selector.select_diverse(k=k)
        else:  # random
            selected = self.selector.select_random(k=k)

        # Format prompt
        if self.formatter_type == "conversational":
            prompt = self.formatter.format_conversational(selected, query)
        elif self.formatter_type == "reasoning":
            prompt = self.formatter.format_with_reasoning(selected, query)
        else:  # basic
            prompt = self.formatter.format_basic(
                selected,
                query,
                instruction=instruction,
                **kwargs
            )

        return FewShotPrompt(
            prompt=prompt,
            examples_used=selected,
            example_count=len(selected)
        )


# Usage Examples
if __name__ == "__main__":
    # Create example pool
    examples = [
        Example(
            input="What is 2 + 2?",
            output="4",
            metadata={"category": "math", "difficulty": "easy"}
        ),
        Example(
            input="What is 10 * 5?",
            output="50",
            metadata={"category": "math", "difficulty": "easy"}
        ),
        Example(
            input="What is the capital of France?",
            output="Paris",
            metadata={"category": "geography", "difficulty": "easy"}
        ),
        Example(
            input="Who wrote Romeo and Juliet?",
            output="William Shakespeare",
            metadata={"category": "literature", "difficulty": "medium"}
        ),
        Example(
            input="What is photosynthesis?",
            output="The process by which plants convert light energy into chemical energy",
            metadata={"category": "science", "difficulty": "medium"}
        )
    ]

    # Example 1: Random selection
    print("=== Random Selection ===")
    selector = ExampleSelector(examples)
    random_examples = selector.select_random(k=2)

    formatter = FewShotFormatter()
    prompt = formatter.format_basic(
        random_examples,
        query="What is 7 + 3?",
        instruction="Solve the following problems:"
    )

    print(prompt)
    print()

    # Example 2: Metadata filtering
    print("=== Metadata Filtering ===")
    math_examples = selector.select_by_metadata(
        {"category": "math"},
        k=2
    )

    prompt2 = formatter.format_basic(
        math_examples,
        query="What is 15 - 8?"
    )

    print(prompt2)
    print()

    # Example 3: Dynamic few-shot
    if EMBEDDINGS_AVAILABLE:
        print("=== Dynamic Few-Shot (Semantic) ===")
        dynamic = DynamicFewShotPrompt(
            examples,
            selector_type="semantic",
            formatter_type="basic"
        )

        few_shot = dynamic.create_prompt(
            query="What is the capital of Germany?",
            k=2
        )

        print(few_shot.prompt)
        print(f"\nExamples used: {few_shot.example_count}")
