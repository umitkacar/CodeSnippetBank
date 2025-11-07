"""
Named Entity Recognition (NER)
Extract entities from text using spaCy and transformers.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class Entity:
    """Container for named entity."""
    text: str
    label: str
    start: int
    end: int
    confidence: Optional[float] = None


@dataclass
class NERResult:
    """Container for NER results."""
    text: str
    entities: List[Entity]


class SpaCyNER:
    """NER using spaCy."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize spaCy NER.

        Args:
            model_name: spaCy model name
        """
        if not SPACY_AVAILABLE:
            raise ImportError("spacy not installed")

        self.nlp = spacy.load(model_name)

    def extract(self, text: str) -> NERResult:
        """
        Extract entities from text.

        Args:
            text: Input text

        Returns:
            NERResult object
        """
        doc = self.nlp(text)

        entities = [
            Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            )
            for ent in doc.ents
        ]

        return NERResult(text=text, entities=entities)


class TransformersNER:
    """NER using transformers."""

    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        """Initialize transformer NER."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers not installed")

        self.ner = pipeline("ner", model=model_name, grouped_entities=True)

    def extract(self, text: str) -> NERResult:
        """Extract entities."""
        results = self.ner(text)

        entities = [
            Entity(
                text=ent["word"],
                label=ent["entity_group"],
                start=ent["start"],
                end=ent["end"],
                confidence=ent["score"]
            )
            for ent in results
        ]

        return NERResult(text=text, entities=entities)


# Usage Example
if __name__ == "__main__":
    text = "Apple Inc. is based in Cupertino, California. Tim Cook is the CEO."

    if SPACY_AVAILABLE:
        print("=== spaCy NER ===")
        ner = SpaCyNER()
        result = ner.extract(text)

        for entity in result.entities:
            print(f"{entity.text}: {entity.label}")

    if TRANSFORMERS_AVAILABLE:
        print("\n=== Transformers NER ===")
        ner = TransformersNER()
        result = ner.extract(text)

        for entity in result.entities:
            print(f"{entity.text}: {entity.label} ({entity.confidence:.2f})")
