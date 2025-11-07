"""
LLM Evaluation Metrics
Comprehensive evaluation metrics for LLM outputs.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re
from collections import Counter
import numpy as np

try:
    from rouge import Rouge
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False

try:
    from bert_score import score as bert_score
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False

try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    metric_name: str
    score: float
    details: Optional[Dict[str, Any]] = None


class TextSimilarityMetrics:
    """Metrics for measuring text similarity."""

    @staticmethod
    def exact_match(prediction: str, reference: str) -> float:
        """
        Exact match score.

        Args:
            prediction: Predicted text
            reference: Reference text

        Returns:
            1.0 if exact match, 0.0 otherwise
        """
        return float(prediction.strip() == reference.strip())

    @staticmethod
    def token_overlap(prediction: str, reference: str) -> float:
        """
        Token overlap F1 score.

        Args:
            prediction: Predicted text
            reference: Reference text

        Returns:
            F1 score of token overlap
        """
        pred_tokens = set(prediction.lower().split())
        ref_tokens = set(reference.lower().split())

        if not ref_tokens:
            return 0.0

        common = pred_tokens & ref_tokens

        if not common:
            return 0.0

        precision = len(common) / len(pred_tokens) if pred_tokens else 0
        recall = len(common) / len(ref_tokens) if ref_tokens else 0

        if precision + recall == 0:
            return 0.0

        f1 = 2 * (precision * recall) / (precision + recall)
        return f1

    @staticmethod
    def bleu_score(
        prediction: str,
        reference: str,
        n: int = 4
    ) -> float:
        """
        BLEU score for text generation.

        Args:
            prediction: Predicted text
            reference: Reference text
            n: Maximum n-gram size

        Returns:
            BLEU score
        """
        if not NLTK_AVAILABLE:
            raise ImportError("nltk not installed")

        pred_tokens = prediction.lower().split()
        ref_tokens = reference.lower().split()

        weights = tuple([1.0/n] * n)
        smoothing = SmoothingFunction().method1

        score = sentence_bleu(
            [ref_tokens],
            pred_tokens,
            weights=weights,
            smoothing_function=smoothing
        )

        return score

    @staticmethod
    def rouge_scores(
        prediction: str,
        reference: str
    ) -> Dict[str, float]:
        """
        ROUGE scores for summarization.

        Args:
            prediction: Predicted text
            reference: Reference text

        Returns:
            Dictionary of ROUGE scores
        """
        if not ROUGE_AVAILABLE:
            raise ImportError("rouge not installed")

        rouge = Rouge()
        scores = rouge.get_scores(prediction, reference)[0]

        return {
            "rouge-1-f": scores["rouge-1"]["f"],
            "rouge-2-f": scores["rouge-2"]["f"],
            "rouge-l-f": scores["rouge-l"]["f"]
        }

    @staticmethod
    def bertscore(
        predictions: List[str],
        references: List[str],
        lang: str = "en"
    ) -> Dict[str, float]:
        """
        BERTScore for semantic similarity.

        Args:
            predictions: List of predicted texts
            references: List of reference texts
            lang: Language code

        Returns:
            Dictionary of BERTScore metrics
        """
        if not BERTSCORE_AVAILABLE:
            raise ImportError("bert-score not installed")

        P, R, F1 = bert_score(predictions, references, lang=lang, verbose=False)

        return {
            "precision": P.mean().item(),
            "recall": R.mean().item(),
            "f1": F1.mean().item()
        }


class FactualityMetrics:
    """Metrics for evaluating factual accuracy."""

    @staticmethod
    def contains_keywords(
        text: str,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> Tuple[float, List[str]]:
        """
        Check if text contains required keywords.

        Args:
            text: Text to check
            keywords: List of required keywords
            case_sensitive: Whether to match case

        Returns:
            Tuple of (score, missing_keywords)
        """
        if not case_sensitive:
            text = text.lower()
            keywords = [k.lower() for k in keywords]

        found = [k for k in keywords if k in text]
        missing = [k for k in keywords if k not in keywords]

        score = len(found) / len(keywords) if keywords else 1.0

        return score, missing

    @staticmethod
    def entity_match(
        prediction: str,
        reference_entities: List[str]
    ) -> Tuple[float, float, float]:
        """
        Compare extracted entities.

        Args:
            prediction: Predicted text
            reference_entities: List of expected entities

        Returns:
            Tuple of (precision, recall, f1)
        """
        # Simple entity extraction (word-based)
        # In production, use NER model
        pred_entities = set(
            word for word in prediction.split()
            if word[0].isupper() and len(word) > 1
        )

        ref_entities = set(reference_entities)

        if not ref_entities:
            return 1.0, 1.0, 1.0

        if not pred_entities:
            return 0.0, 0.0, 0.0

        correct = pred_entities & ref_entities

        precision = len(correct) / len(pred_entities)
        recall = len(correct) / len(ref_entities)

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        return precision, recall, f1


class CoherenceMetrics:
    """Metrics for evaluating text coherence."""

    @staticmethod
    def sentence_count(text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])

    @staticmethod
    def avg_sentence_length(text: str) -> float:
        """Calculate average sentence length."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)

    @staticmethod
    def lexical_diversity(text: str) -> float:
        """
        Calculate lexical diversity (unique words / total words).

        Args:
            text: Input text

        Returns:
            Lexical diversity score
        """
        words = text.lower().split()

        if not words:
            return 0.0

        unique_words = set(words)
        return len(unique_words) / len(words)

    @staticmethod
    def repetition_score(text: str, n: int = 2) -> float:
        """
        Calculate repetition score for n-grams.

        Args:
            text: Input text
            n: N-gram size

        Returns:
            Repetition score (lower is better)
        """
        words = text.lower().split()

        if len(words) < n:
            return 0.0

        # Generate n-grams
        ngrams = [
            tuple(words[i:i+n])
            for i in range(len(words) - n + 1)
        ]

        if not ngrams:
            return 0.0

        # Count frequencies
        counts = Counter(ngrams)

        # Calculate repetition (proportion of repeated n-grams)
        repeated = sum(1 for count in counts.values() if count > 1)
        repetition = repeated / len(counts) if counts else 0.0

        return repetition


class LLMEvaluator:
    """Comprehensive LLM output evaluator."""

    def __init__(self):
        """Initialize evaluator."""
        self.similarity = TextSimilarityMetrics()
        self.factuality = FactualityMetrics()
        self.coherence = CoherenceMetrics()

    def evaluate_generation(
        self,
        prediction: str,
        reference: Optional[str] = None,
        required_keywords: Optional[List[str]] = None
    ) -> List[EvaluationResult]:
        """
        Comprehensive evaluation of generated text.

        Args:
            prediction: Generated text
            reference: Optional reference text
            required_keywords: Optional required keywords

        Returns:
            List of EvaluationResult objects
        """
        results = []

        # Coherence metrics (always computed)
        results.append(EvaluationResult(
            metric_name="sentence_count",
            score=self.coherence.sentence_count(prediction)
        ))

        results.append(EvaluationResult(
            metric_name="avg_sentence_length",
            score=self.coherence.avg_sentence_length(prediction)
        ))

        results.append(EvaluationResult(
            metric_name="lexical_diversity",
            score=self.coherence.lexical_diversity(prediction)
        ))

        results.append(EvaluationResult(
            metric_name="repetition_score",
            score=self.coherence.repetition_score(prediction)
        ))

        # Similarity metrics (if reference provided)
        if reference:
            results.append(EvaluationResult(
                metric_name="exact_match",
                score=self.similarity.exact_match(prediction, reference)
            ))

            results.append(EvaluationResult(
                metric_name="token_overlap_f1",
                score=self.similarity.token_overlap(prediction, reference)
            ))

            if ROUGE_AVAILABLE:
                try:
                    rouge_scores = self.similarity.rouge_scores(prediction, reference)
                    for metric, score in rouge_scores.items():
                        results.append(EvaluationResult(
                            metric_name=metric,
                            score=score
                        ))
                except:
                    pass

        # Factuality metrics (if keywords provided)
        if required_keywords:
            score, missing = self.factuality.contains_keywords(
                prediction,
                required_keywords
            )
            results.append(EvaluationResult(
                metric_name="keyword_coverage",
                score=score,
                details={"missing_keywords": missing}
            ))

        return results

    def print_evaluation(self, results: List[EvaluationResult]):
        """Print evaluation results in readable format."""
        print("=" * 50)
        print("LLM Evaluation Results")
        print("=" * 50)

        for result in results:
            print(f"\n{result.metric_name}:")
            print(f"  Score: {result.score:.4f}")

            if result.details:
                print(f"  Details: {result.details}")


# Usage Examples
if __name__ == "__main__":
    evaluator = LLMEvaluator()

    # Example 1: Simple evaluation
    prediction = "Python is a popular programming language. It is easy to learn and versatile."
    reference = "Python is a widely-used programming language known for its simplicity and flexibility."

    results = evaluator.evaluate_generation(
        prediction=prediction,
        reference=reference
    )

    evaluator.print_evaluation(results)

    # Example 2: With keywords
    print("\n" + "=" * 50)
    print("Evaluation with Required Keywords")
    print("=" * 50)

    prediction2 = "Machine learning models can be trained on large datasets to make predictions."
    keywords = ["machine learning", "models", "datasets", "predictions", "accuracy"]

    results2 = evaluator.evaluate_generation(
        prediction=prediction2,
        required_keywords=keywords
    )

    evaluator.print_evaluation(results2)

    # Example 3: Coherence only
    print("\n" + "=" * 50)
    print("Coherence Metrics Only")
    print("=" * 50)

    prediction3 = """
    Artificial intelligence is transforming industries. AI systems can process data quickly.
    Machine learning is a subset of AI. Deep learning uses neural networks.
    These technologies are advancing rapidly.
    """

    results3 = evaluator.evaluate_generation(prediction=prediction3)
    evaluator.print_evaluation(results3)
