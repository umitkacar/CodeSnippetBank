"""
LLM Cost Tracking and Optimization
Track and optimize API costs across different LLM providers.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class ModelProvider(Enum):
    """LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"


@dataclass
class ModelPricing:
    """Pricing information for a model."""
    model_name: str
    provider: ModelProvider
    input_cost_per_1k: float  # USD per 1K input tokens
    output_cost_per_1k: float  # USD per 1K output tokens
    context_window: int


# Current pricing (as of 2024 - update regularly)
PRICING_DATABASE = {
    # OpenAI
    "gpt-4-turbo-preview": ModelPricing(
        "gpt-4-turbo-preview",
        ModelProvider.OPENAI,
        0.01,  # $0.01 per 1K input tokens
        0.03,  # $0.03 per 1K output tokens
        128000
    ),
    "gpt-4": ModelPricing(
        "gpt-4",
        ModelProvider.OPENAI,
        0.03,
        0.06,
        8192
    ),
    "gpt-3.5-turbo": ModelPricing(
        "gpt-3.5-turbo",
        ModelProvider.OPENAI,
        0.0005,
        0.0015,
        16385
    ),

    # Anthropic
    "claude-3-opus-20240229": ModelPricing(
        "claude-3-opus",
        ModelProvider.ANTHROPIC,
        0.015,
        0.075,
        200000
    ),
    "claude-3-sonnet-20240229": ModelPricing(
        "claude-3-sonnet",
        ModelProvider.ANTHROPIC,
        0.003,
        0.015,
        200000
    ),
    "claude-3-haiku-20240307": ModelPricing(
        "claude-3-haiku",
        ModelProvider.ANTHROPIC,
        0.00025,
        0.00125,
        200000
    ),

    # Google
    "gemini-pro": ModelPricing(
        "gemini-pro",
        ModelProvider.GOOGLE,
        0.000125,
        0.000375,
        32760
    ),
}


@dataclass
class UsageRecord:
    """Record of LLM usage."""
    timestamp: datetime
    model: str
    provider: ModelProvider
    input_tokens: int
    output_tokens: int
    cost: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CostSummary:
    """Summary of costs."""
    total_cost: float
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    cost_by_provider: Dict[str, float] = field(default_factory=dict)


class CostTracker:
    """Track LLM API costs."""

    def __init__(self):
        """Initialize cost tracker."""
        self.usage_records: List[UsageRecord] = []

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict] = None
    ) -> float:
        """
        Record usage and calculate cost.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Optional metadata

        Returns:
            Cost in USD
        """
        if model not in PRICING_DATABASE:
            raise ValueError(f"Unknown model: {model}")

        pricing = PRICING_DATABASE[model]

        # Calculate cost
        input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
        total_cost = input_cost + output_cost

        # Record usage
        record = UsageRecord(
            timestamp=datetime.now(),
            model=model,
            provider=pricing.provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=total_cost,
            metadata=metadata
        )

        self.usage_records.append(record)

        return total_cost

    def get_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CostSummary:
        """
        Get cost summary for date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            CostSummary object
        """
        # Filter records
        records = self.usage_records

        if start_date:
            records = [r for r in records if r.timestamp >= start_date]

        if end_date:
            records = [r for r in records if r.timestamp <= end_date]

        # Calculate totals
        total_cost = sum(r.cost for r in records)
        total_input = sum(r.input_tokens for r in records)
        total_output = sum(r.output_tokens for r in records)

        # Group by model
        cost_by_model: Dict[str, float] = {}
        for record in records:
            if record.model not in cost_by_model:
                cost_by_model[record.model] = 0
            cost_by_model[record.model] += record.cost

        # Group by provider
        cost_by_provider: Dict[str, float] = {}
        for record in records:
            provider_name = record.provider.value
            if provider_name not in cost_by_provider:
                cost_by_provider[provider_name] = 0
            cost_by_provider[provider_name] += record.cost

        return CostSummary(
            total_cost=total_cost,
            total_requests=len(records),
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            cost_by_model=cost_by_model,
            cost_by_provider=cost_by_provider
        )

    def export_to_json(self, filepath: str):
        """Export usage records to JSON."""
        data = [
            {
                "timestamp": record.timestamp.isoformat(),
                "model": record.model,
                "provider": record.provider.value,
                "input_tokens": record.input_tokens,
                "output_tokens": record.output_tokens,
                "cost": record.cost,
                "metadata": record.metadata
            }
            for record in self.usage_records
        ]

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


class CostOptimizer:
    """Optimize costs by suggesting cheaper alternatives."""

    @staticmethod
    def suggest_alternative(
        model: str,
        max_budget: float,
        min_context_window: int = 4000
    ) -> List[str]:
        """
        Suggest cheaper alternative models.

        Args:
            model: Current model
            max_budget: Maximum budget per 1K tokens
            min_context_window: Minimum required context window

        Returns:
            List of suggested model names
        """
        if model not in PRICING_DATABASE:
            return []

        current_pricing = PRICING_DATABASE[model]
        suggestions = []

        for model_name, pricing in PRICING_DATABASE.items():
            if model_name == model:
                continue

            # Check if cheaper
            avg_cost = (pricing.input_cost_per_1k + pricing.output_cost_per_1k) / 2
            current_avg = (current_pricing.input_cost_per_1k + current_pricing.output_cost_per_1k) / 2

            if avg_cost < current_avg and avg_cost <= max_budget:
                if pricing.context_window >= min_context_window:
                    suggestions.append(model_name)

        # Sort by cost (cheapest first)
        suggestions.sort(key=lambda m: PRICING_DATABASE[m].input_cost_per_1k)

        return suggestions

    @staticmethod
    def estimate_cost(
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for a request.

        Args:
            model: Model name
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens

        Returns:
            Estimated cost in USD
        """
        if model not in PRICING_DATABASE:
            raise ValueError(f"Unknown model: {model}")

        pricing = PRICING_DATABASE[model]

        input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k

        return input_cost + output_cost

    @staticmethod
    def compare_models(
        models: List[str],
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, float]:
        """
        Compare costs across models.

        Args:
            models: List of model names
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            Dictionary of model -> cost
        """
        comparisons = {}

        for model in models:
            if model in PRICING_DATABASE:
                cost = CostOptimizer.estimate_cost(model, input_tokens, output_tokens)
                comparisons[model] = cost

        return dict(sorted(comparisons.items(), key=lambda x: x[1]))


class BudgetManager:
    """Manage and enforce budget limits."""

    def __init__(
        self,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None
    ):
        """
        Initialize budget manager.

        Args:
            daily_budget: Daily budget in USD
            monthly_budget: Monthly budget in USD
        """
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.tracker = CostTracker()

    def can_make_request(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int
    ) -> Tuple[bool, str]:
        """
        Check if request is within budget.

        Args:
            model: Model to use
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            Tuple of (can_proceed, reason)
        """
        estimated_cost = CostOptimizer.estimate_cost(
            model,
            estimated_input_tokens,
            estimated_output_tokens
        )

        # Check daily budget
        if self.daily_budget:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_summary = self.tracker.get_summary(start_date=today)

            if today_summary.total_cost + estimated_cost > self.daily_budget:
                return False, f"Would exceed daily budget (${self.daily_budget})"

        # Check monthly budget
        if self.monthly_budget:
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_summary = self.tracker.get_summary(start_date=month_start)

            if month_summary.total_cost + estimated_cost > self.monthly_budget:
                return False, f"Would exceed monthly budget (${self.monthly_budget})"

        return True, "OK"


# Usage Examples
if __name__ == "__main__":
    # Example 1: Track costs
    print("=== Cost Tracking ===")
    tracker = CostTracker()

    # Record some usage
    cost1 = tracker.record_usage("gpt-4-turbo-preview", 1000, 500)
    print(f"GPT-4 Turbo cost: ${cost1:.4f}")

    cost2 = tracker.record_usage("gpt-3.5-turbo", 1000, 500)
    print(f"GPT-3.5 Turbo cost: ${cost2:.4f}")

    cost3 = tracker.record_usage("claude-3-sonnet-20240229", 1000, 500)
    print(f"Claude 3 Sonnet cost: ${cost3:.4f}\n")

    # Get summary
    summary = tracker.get_summary()
    print(f"Total cost: ${summary.total_cost:.4f}")
    print(f"Total requests: {summary.total_requests}")
    print(f"Cost by model: {summary.cost_by_model}\n")

    # Example 2: Optimize costs
    print("=== Cost Optimization ===")

    alternatives = CostOptimizer.suggest_alternative(
        "gpt-4",
        max_budget=0.01,
        min_context_window=4000
    )

    print(f"Cheaper alternatives to GPT-4: {alternatives}\n")

    # Example 3: Compare models
    print("=== Model Comparison ===")
    models_to_compare = ["gpt-4", "gpt-3.5-turbo", "claude-3-haiku-20240307"]
    comparison = CostOptimizer.compare_models(models_to_compare, 1000, 500)

    for model, cost in comparison.items():
        print(f"{model}: ${cost:.4f}")
    print()

    # Example 4: Budget management
    print("=== Budget Management ===")
    budget = BudgetManager(daily_budget=10.0)

    can_proceed, reason = budget.can_make_request("gpt-4", 10000, 5000)
    estimated = CostOptimizer.estimate_cost("gpt-4", 10000, 5000)

    print(f"Can make request: {can_proceed}")
    print(f"Reason: {reason}")
    print(f"Estimated cost: ${estimated:.4f}")
