"""
Multi-Model Routing
Intelligently route requests to different LLMs based on requirements.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class TaskType(Enum):
    """Types of tasks."""
    GENERAL_QA = "general_qa"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    MATH = "math"
    REASONING = "reasoning"


@dataclass
class ModelCapability:
    """Model capability profile."""
    model_name: str
    provider: str
    max_tokens: int
    context_window: int
    cost_per_1k: float
    speed_rank: int  # 1 = fastest
    quality_rank: int  # 1 = highest quality
    best_for: List[TaskType]
    supported_languages: List[str]


# Model profiles
MODEL_PROFILES = {
    "gpt-4-turbo": ModelCapability(
        model_name="gpt-4-turbo-preview",
        provider="openai",
        max_tokens=4096,
        context_window=128000,
        cost_per_1k=0.02,
        speed_rank=3,
        quality_rank=1,
        best_for=[TaskType.REASONING, TaskType.CODE_GENERATION, TaskType.ANALYSIS],
        supported_languages=["en", "es", "fr", "de", "zh", "ja"]
    ),
    "gpt-3.5-turbo": ModelCapability(
        model_name="gpt-3.5-turbo",
        provider="openai",
        max_tokens=4096,
        context_window=16385,
        cost_per_1k=0.001,
        speed_rank=1,
        quality_rank=3,
        best_for=[TaskType.GENERAL_QA, TaskType.SUMMARIZATION, TaskType.TRANSLATION],
        supported_languages=["en", "es", "fr", "de", "zh", "ja"]
    ),
    "claude-opus": ModelCapability(
        model_name="claude-3-opus-20240229",
        provider="anthropic",
        max_tokens=4096,
        context_window=200000,
        cost_per_1k=0.045,
        speed_rank=4,
        quality_rank=1,
        best_for=[TaskType.CREATIVE_WRITING, TaskType.ANALYSIS, TaskType.REASONING],
        supported_languages=["en", "es", "fr", "de", "zh", "ja"]
    ),
    "claude-haiku": ModelCapability(
        model_name="claude-3-haiku-20240307",
        provider="anthropic",
        max_tokens=4096,
        context_window=200000,
        cost_per_1k=0.0007,
        speed_rank=1,
        quality_rank=4,
        best_for=[TaskType.GENERAL_QA, TaskType.SUMMARIZATION],
        supported_languages=["en", "es", "fr", "de"]
    ),
    "gemini-pro": ModelCapability(
        model_name="gemini-pro",
        provider="google",
        max_tokens=2048,
        context_window=32760,
        cost_per_1k=0.00025,
        speed_rank=2,
        quality_rank=3,
        best_for=[TaskType.GENERAL_QA, TaskType.SUMMARIZATION],
        supported_languages=["en", "es", "fr", "de", "zh", "ja"]
    )
}


class TaskClassifier:
    """Classify tasks to determine routing."""

    @staticmethod
    def classify_complexity(prompt: str) -> TaskComplexity:
        """
        Classify task complexity from prompt.

        Args:
            prompt: User prompt

        Returns:
            TaskComplexity level
        """
        # Simple heuristics
        word_count = len(prompt.split())

        # Check for complexity indicators
        complex_indicators = [
            "analyze", "compare", "evaluate", "critique",
            "complex", "detailed", "comprehensive", "in-depth"
        ]

        medium_indicators = [
            "explain", "describe", "outline", "summarize"
        ]

        prompt_lower = prompt.lower()

        if any(ind in prompt_lower for ind in complex_indicators):
            return TaskComplexity.COMPLEX

        if any(ind in prompt_lower for ind in medium_indicators):
            return TaskComplexity.MEDIUM

        if word_count > 100:
            return TaskComplexity.COMPLEX
        elif word_count > 30:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.SIMPLE

    @staticmethod
    def classify_task_type(prompt: str) -> TaskType:
        """
        Classify task type from prompt.

        Args:
            prompt: User prompt

        Returns:
            TaskType
        """
        prompt_lower = prompt.lower()

        # Code generation indicators
        if any(word in prompt_lower for word in ["code", "function", "class", "implement", "program"]):
            return TaskType.CODE_GENERATION

        # Creative writing indicators
        if any(word in prompt_lower for word in ["story", "poem", "creative", "write"]):
            return TaskType.CREATIVE_WRITING

        # Math indicators
        if any(word in prompt_lower for word in ["calculate", "solve", "equation", "math"]):
            return TaskType.MATH

        # Analysis indicators
        if any(word in prompt_lower for word in ["analyze", "compare", "evaluate"]):
            return TaskType.ANALYSIS

        # Summarization indicators
        if any(word in prompt_lower for word in ["summarize", "summary", "brief"]):
            return TaskType.SUMMARIZATION

        # Translation indicators
        if any(word in prompt_lower for word in ["translate", "translation"]):
            return TaskType.TRANSLATION

        # Default
        return TaskType.GENERAL_QA


class ModelRouter:
    """Route requests to appropriate models."""

    def __init__(
        self,
        models: Optional[Dict[str, ModelCapability]] = None,
        prefer_speed: bool = False,
        prefer_quality: bool = True,
        budget_limit: Optional[float] = None
    ):
        """
        Initialize model router.

        Args:
            models: Available models (defaults to MODEL_PROFILES)
            prefer_speed: Prefer faster models
            prefer_quality: Prefer higher quality models
            budget_limit: Maximum cost per 1K tokens
        """
        self.models = models or MODEL_PROFILES
        self.prefer_speed = prefer_speed
        self.prefer_quality = prefer_quality
        self.budget_limit = budget_limit
        self.classifier = TaskClassifier()

    def route(
        self,
        prompt: str,
        context_length: Optional[int] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Route prompt to best model.

        Args:
            prompt: User prompt
            context_length: Length of context in tokens
            max_tokens: Maximum tokens needed

        Returns:
            Selected model name
        """
        # Classify task
        complexity = self.classifier.classify_complexity(prompt)
        task_type = self.classifier.classify_task_type(prompt)

        # Filter suitable models
        suitable_models = []

        for model_id, model in self.models.items():
            # Check budget
            if self.budget_limit and model.cost_per_1k > self.budget_limit:
                continue

            # Check context window
            if context_length and model.context_window < context_length:
                continue

            # Check max tokens
            if max_tokens and model.max_tokens < max_tokens:
                continue

            # Check task suitability
            if task_type in model.best_for:
                suitable_models.append((model_id, model))

        if not suitable_models:
            # Fallback to any model that meets basic requirements
            suitable_models = [
                (mid, m) for mid, m in self.models.items()
                if (not context_length or m.context_window >= context_length)
                and (not max_tokens or m.max_tokens >= max_tokens)
                and (not self.budget_limit or m.cost_per_1k <= self.budget_limit)
            ]

        if not suitable_models:
            raise ValueError("No suitable model found for requirements")

        # Score and select
        best_model = self._score_and_select(suitable_models, complexity)

        return best_model

    def _score_and_select(
        self,
        models: List[tuple],
        complexity: TaskComplexity
    ) -> str:
        """Score models and select best."""
        scores = []

        for model_id, model in models:
            score = 0

            # Complexity-based scoring
            if complexity == TaskComplexity.SIMPLE:
                score += 10 / model.speed_rank  # Prefer speed
                score -= model.cost_per_1k * 100  # Prefer low cost
            elif complexity == TaskComplexity.MEDIUM:
                score += 5 / model.speed_rank
                score += 5 / model.quality_rank
            else:  # COMPLEX
                score += 10 / model.quality_rank  # Prefer quality
                score += 3 / model.speed_rank

            # Preferences
            if self.prefer_speed:
                score += 5 / model.speed_rank

            if self.prefer_quality:
                score += 5 / model.quality_rank

            scores.append((model_id, score))

        # Select highest score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]


class AdaptiveRouter:
    """Router that learns from feedback."""

    def __init__(self, base_router: ModelRouter):
        """
        Initialize adaptive router.

        Args:
            base_router: Base router to use
        """
        self.base_router = base_router
        self.feedback_history: List[Dict[str, Any]] = []

    def route_with_feedback(
        self,
        prompt: str,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Route and return routing ID for feedback.

        Args:
            prompt: User prompt
            **kwargs: Additional routing parameters

        Returns:
            Tuple of (model_name, routing_id)
        """
        model = self.base_router.route(prompt, **kwargs)
        routing_id = f"route_{len(self.feedback_history)}"

        self.feedback_history.append({
            "routing_id": routing_id,
            "prompt": prompt,
            "model": model,
            "feedback": None
        })

        return model, routing_id

    def record_feedback(
        self,
        routing_id: str,
        success: bool,
        quality_score: Optional[float] = None
    ):
        """
        Record feedback for a routing decision.

        Args:
            routing_id: Routing ID from route_with_feedback
            success: Whether routing was successful
            quality_score: Optional quality score (0-1)
        """
        for record in self.feedback_history:
            if record["routing_id"] == routing_id:
                record["feedback"] = {
                    "success": success,
                    "quality_score": quality_score
                }
                break


# Usage Examples
if __name__ == "__main__":
    # Example 1: Simple routing
    print("=== Simple Routing ===")

    router = ModelRouter()

    prompts = [
        "What is Python?",  # Simple QA
        "Write a complex sorting algorithm in Python with detailed analysis",  # Complex code
        "Summarize this article",  # Summarization
        "Write a creative story about AI"  # Creative writing
    ]

    for prompt in prompts:
        model = router.route(prompt)
        complexity = router.classifier.classify_complexity(prompt)
        task_type = router.classifier.classify_task_type(prompt)

        print(f"\nPrompt: {prompt[:50]}...")
        print(f"Complexity: {complexity.value}")
        print(f"Task Type: {task_type.value}")
        print(f"Selected Model: {model}")

    # Example 2: Budget-constrained routing
    print("\n\n=== Budget-Constrained Routing ===")

    budget_router = ModelRouter(budget_limit=0.005)

    complex_prompt = "Provide a comprehensive analysis of quantum computing"
    try:
        model = budget_router.route(complex_prompt)
        print(f"Selected model within budget: {model}")
    except ValueError as e:
        print(f"Error: {e}")

    # Example 3: Speed-preferring routing
    print("\n=== Speed-Preferring Routing ===")

    speed_router = ModelRouter(prefer_speed=True, prefer_quality=False)

    fast_prompt = "Quick question: what's 2+2?"
    model = speed_router.route(fast_prompt)
    print(f"Speed-optimized model: {model}")

    # Example 4: Adaptive routing with feedback
    print("\n=== Adaptive Routing ===")

    adaptive = AdaptiveRouter(router)

    model, routing_id = adaptive.route_with_feedback("Explain machine learning")
    print(f"Routed to: {model}")
    print(f"Routing ID: {routing_id}")

    # Record feedback
    adaptive.record_feedback(routing_id, success=True, quality_score=0.9)
    print("Feedback recorded")
