"""
Transformers Text Classification
Fine-tune and use transformer models for text classification.
"""

import torch
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        Trainer,
        TrainingArguments,
        pipeline
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class ClassificationResult:
    """Container for classification result."""
    text: str
    label: str
    score: float
    all_scores: Optional[Dict[str, float]] = None


class TextClassifier:
    """Production-ready text classifier using transformers."""

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        num_labels: int = 2,
        device: str = "cpu"
    ):
        """
        Initialize classifier.

        Args:
            model_name: HuggingFace model name
            num_labels: Number of classes
            device: Device to use
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers not installed")

        self.model_name = model_name
        self.device = device

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )

        self.model.to(device)

    def predict(
        self,
        texts: List[str],
        labels: Optional[List[str]] = None
    ) -> List[ClassificationResult]:
        """
        Predict classes for texts.

        Args:
            texts: List of texts to classify
            labels: Optional label names

        Returns:
            List of ClassificationResult objects
        """
        # Tokenize
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get predictions
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        results = []

        for i, text in enumerate(texts):
            scores = predictions[i].cpu().numpy()
            predicted_class = int(scores.argmax())

            # Get label name
            if labels:
                label = labels[predicted_class]
            else:
                label = str(predicted_class)

            # Get all scores
            all_scores = {}

            if labels:
                for j, label_name in enumerate(labels):
                    all_scores[label_name] = float(scores[j])

            result = ClassificationResult(
                text=text,
                label=label,
                score=float(scores[predicted_class]),
                all_scores=all_scores if labels else None
            )

            results.append(result)

        return results

    def train(
        self,
        train_texts: List[str],
        train_labels: List[int],
        output_dir: str,
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ):
        """
        Fine-tune model on custom data.

        Args:
            train_texts: Training texts
            train_labels: Training labels (as integers)
            output_dir: Output directory
            num_epochs: Number of epochs
            batch_size: Batch size
            learning_rate: Learning rate
        """
        # Create dataset
        dataset = Dataset.from_dict({
            "text": train_texts,
            "label": train_labels
        })

        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512
            )

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            logging_steps=100,
            save_steps=500,
            evaluation_strategy="no"
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset
        )

        # Train
        trainer.train()

        # Save
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)


class SentimentAnalyzer:
    """Sentiment analysis using pre-trained models."""

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """Initialize sentiment analyzer."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers not installed")

        self.classifier = pipeline(
            "sentiment-analysis",
            model=model_name
        )

    def analyze(self, texts: List[str]) -> List[ClassificationResult]:
        """
        Analyze sentiment of texts.

        Args:
            texts: List of texts

        Returns:
            List of ClassificationResult objects
        """
        results = self.classifier(texts)

        return [
            ClassificationResult(
                text=text,
                label=result["label"],
                score=result["score"]
            )
            for text, result in zip(texts, results)
        ]


# Usage Examples
if __name__ == "__main__":
    if not TRANSFORMERS_AVAILABLE:
        print("Please install transformers: pip install transformers datasets")
        exit(1)

    print("=== Text Classification ===")

    # Example 1: Sentiment Analysis
    print("\n=== Sentiment Analysis ===")

    sentiment = SentimentAnalyzer()

    texts = [
        "I love this product, it's amazing!",
        "This is terrible, waste of money.",
        "It's okay, nothing special."
    ]

    results = sentiment.analyze(texts)

    for result in results:
        print(f"Text: {result.text}")
        print(f"Sentiment: {result.label} ({result.score:.2f})\n")

    # Example 2: Custom Classification
    print("=== Custom Classifier ===")

    classifier = TextClassifier(
        model_name="distilbert-base-uncased",
        num_labels=3  # 3 classes
    )

    # Predict
    test_texts = ["This is a test", "Another example"]
    labels = ["Class A", "Class B", "Class C"]

    predictions = classifier.predict(test_texts, labels)

    for pred in predictions:
        print(f"Text: {pred.text}")
        print(f"Predicted: {pred.label} ({pred.score:.2f})")
        if pred.all_scores:
            print(f"All scores: {pred.all_scores}")
        print()

    print("Text classification ready!")
