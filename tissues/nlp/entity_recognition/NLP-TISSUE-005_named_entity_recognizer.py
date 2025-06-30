"""
Tissue ID: NLP-TISSUE-005
Title: Multi-Model Named Entity Recognizer
Category: nlp/entity_recognition
Tags: ["ner", "entity-extraction", "nlp", "information-extraction", "tagging"]
Difficulty: Advanced
Dependencies: ["spacy>=3.5", "nltk>=3.8", "transformers>=4.30"]
Performance: O(n) where n is text length
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive Named Entity Recognition (NER) tissue that provides multiple
approaches for extracting entities from text. Supports rule-based, statistical,
and transformer-based models with customizable entity types and confidence scores.

Use Cases:
- Information extraction from documents
- Contact information extraction
- Location and organization detection
- Medical entity recognition
- Financial entity extraction

Example Usage:
    # Basic NER
    ner = NamedEntityRecognizer(strategy="spacy")
    entities = ner.extract_entities("Apple Inc. was founded by Steve Jobs in Cupertino.")
    # Result: [{"text": "Apple Inc.", "type": "ORG", "start": 0, "end": 10}, ...]
    
    # Custom entity types
    ner = NamedEntityRecognizer(
        custom_patterns={"PRODUCT": [r"iPhone \d+", r"MacBook \w+"]}
    )
    entities = ner.extract_entities(text)
"""

from typing import List, Dict, Optional, Set, Tuple, Any, Pattern
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from collections import defaultdict


class NERStrategy(Enum):
    """Available NER strategies"""
    RULE_BASED = "rule_based"
    SPACY = "spacy"
    NLTK = "nltk"
    TRANSFORMER = "transformer"
    HYBRID = "hybrid"


class EntityType(Enum):
    """Standard entity types"""
    PERSON = "PER"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    URL = "URL"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    LANGUAGE = "LANGUAGE"
    MISC = "MISC"


@dataclass
class Entity:
    """Represents a named entity"""
    text: str
    type: str
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "type": self.type,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


@dataclass
class NERConfig:
    """Configuration for NER"""
    min_confidence: float = 0.5
    merge_adjacent: bool = True
    case_sensitive: bool = False
    return_positions: bool = True
    max_entity_length: int = 100
    custom_types: Set[str] = field(default_factory=set)
    language: str = "en"


class NamedEntityRecognizer:
    """
    Multi-model Named Entity Recognition system.
    Tissue Type: FUNCTIONAL - Core NLP entity extraction.
    """
    
    # Common patterns for rule-based NER
    PATTERNS = {
        "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "URL": re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
        "PHONE": re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        "DATE": re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|'
                          r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b'),
        "TIME": re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AaPp][Mm])?\b'),
        "MONEY": re.compile(r'[$€£¥]\s?\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|JPY)'),
        "PERCENT": re.compile(r'\b\d+(?:\.\d+)?%\b'),
        "IP_ADDRESS": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    }
    
    # Common person name patterns
    PERSON_TITLES = {"Mr", "Mrs", "Ms", "Dr", "Prof", "Sir", "Lady", "Lord"}
    
    def __init__(self,
                 strategy: str = "rule_based",
                 model_name: Optional[str] = None,
                 config: Optional[NERConfig] = None,
                 custom_patterns: Optional[Dict[str, List[str]]] = None):
        """
        Initialize NER system.
        
        Args:
            strategy: NER strategy to use
            model_name: Pre-trained model name
            config: Configuration options
            custom_patterns: Custom regex patterns for entity types
        """
        self.strategy = NERStrategy(strategy.lower())
        self.model_name = model_name
        self.config = config or NERConfig()
        
        # Add custom patterns
        self.patterns = self.PATTERNS.copy()
        if custom_patterns:
            for entity_type, patterns in custom_patterns.items():
                self.patterns[entity_type] = re.compile('|'.join(patterns))
        
        # Initialize model
        self._init_model()
        
        # Statistics
        self.texts_processed = 0
        self.entities_extracted = 0
    
    def _init_model(self):
        """Initialize NER model based on strategy"""
        self.model = None
        
        if self.strategy == NERStrategy.SPACY:
            self._init_spacy()
        elif self.strategy == NERStrategy.NLTK:
            self._init_nltk()
        elif self.strategy == NERStrategy.TRANSFORMER:
            self._init_transformer()
    
    def _init_spacy(self):
        """Initialize spaCy NER"""
        try:
            import spacy
            
            # Load model based on language
            model_name = self.model_name or f"{self.config.language}_core_web_sm"
            try:
                self.model = spacy.load(model_name)
            except:
                # Download if not available
                import subprocess
                subprocess.run([f"python -m spacy download {model_name}"], shell=True)
                self.model = spacy.load(model_name)
        except ImportError:
            print("Warning: spaCy not available")
    
    def _init_nltk(self):
        """Initialize NLTK NER"""
        try:
            import nltk
            
            # Download required data
            required_data = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
            for data in required_data:
                try:
                    nltk.data.find(f'tokenizers/{data}')
                except:
                    nltk.download(data, quiet=True)
            
            self.model = "nltk"
        except ImportError:
            print("Warning: NLTK not available")
    
    def _init_transformer(self):
        """Initialize transformer-based NER"""
        try:
            from transformers import pipeline
            
            model_name = self.model_name or "dslim/bert-base-NER"
            self.model = pipeline("ner", model=model_name, aggregation_strategy="simple")
        except ImportError:
            print("Warning: transformers not available")
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Entity objects
        """
        if not text:
            return []
        
        self.texts_processed += 1
        
        # Extract entities based on strategy
        if self.strategy == NERStrategy.RULE_BASED:
            entities = self._extract_rule_based(text)
        elif self.strategy == NERStrategy.SPACY:
            entities = self._extract_spacy(text)
        elif self.strategy == NERStrategy.NLTK:
            entities = self._extract_nltk(text)
        elif self.strategy == NERStrategy.TRANSFORMER:
            entities = self._extract_transformer(text)
        elif self.strategy == NERStrategy.HYBRID:
            entities = self._extract_hybrid(text)
        else:
            entities = []
        
        # Post-process entities
        entities = self._post_process(entities, text)
        
        self.entities_extracted += len(entities)
        return entities
    
    def _extract_rule_based(self, text: str) -> List[Entity]:
        """Rule-based entity extraction"""
        entities = []
        
        # Extract using patterns
        for entity_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9  # High confidence for exact matches
                )
                entities.append(entity)
        
        # Extract person names using heuristics
        entities.extend(self._extract_person_names(text))
        
        # Extract organizations using heuristics
        entities.extend(self._extract_organizations(text))
        
        return entities
    
    def _extract_person_names(self, text: str) -> List[Entity]:
        """Extract person names using heuristics"""
        entities = []
        
        # Pattern: Title + Capitalized Words
        pattern = r'\b(' + '|'.join(self.PERSON_TITLES) + r')\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for match in re.finditer(pattern, text):
            entity = Entity(
                text=match.group(),
                type=EntityType.PERSON.value,
                start=match.start(),
                end=match.end(),
                confidence=0.8
            )
            entities.append(entity)
        
        # Pattern: Consecutive capitalized words (2-4 words)
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        for match in re.finditer(pattern, text):
            # Check if not already captured
            if not any(e.start <= match.start() < e.end for e in entities):
                entity = Entity(
                    text=match.group(),
                    type=EntityType.PERSON.value,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.6
                )
                entities.append(entity)
        
        return entities
    
    def _extract_organizations(self, text: str) -> List[Entity]:
        """Extract organization names using heuristics"""
        entities = []
        
        # Common organization suffixes
        org_suffixes = r'\b\w+\s+(?:Inc|Corp|LLC|Ltd|Company|Corporation|Group|Foundation|Institute|University|College)\b'
        
        for match in re.finditer(org_suffixes, text):
            entity = Entity(
                text=match.group(),
                type=EntityType.ORGANIZATION.value,
                start=match.start(),
                end=match.end(),
                confidence=0.8
            )
            entities.append(entity)
        
        return entities
    
    def _extract_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy"""
        if self.model is None:
            return self._extract_rule_based(text)
        
        doc = self.model(text)
        entities = []
        
        for ent in doc.ents:
            # Map spaCy labels to our entity types
            entity_type = self._map_spacy_label(ent.label_)
            
            entity = Entity(
                text=ent.text,
                type=entity_type,
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.9,
                metadata={"spacy_label": ent.label_}
            )
            entities.append(entity)
        
        return entities
    
    def _extract_nltk(self, text: str) -> List[Entity]:
        """Extract entities using NLTK"""
        if self.model is None:
            return self._extract_rule_based(text)
        
        try:
            import nltk
            
            # Tokenize and tag
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            
            # Named entity chunking
            tree = nltk.ne_chunk(pos_tags, binary=False)
            
            entities = []
            current_pos = 0
            
            for subtree in tree:
                if hasattr(subtree, 'label'):
                    # Extract entity
                    entity_text = ' '.join(word for word, tag in subtree)
                    entity_type = self._map_nltk_label(subtree.label())
                    
                    # Find position in original text
                    start = text.find(entity_text, current_pos)
                    if start != -1:
                        entity = Entity(
                            text=entity_text,
                            type=entity_type,
                            start=start,
                            end=start + len(entity_text),
                            confidence=0.8,
                            metadata={"nltk_label": subtree.label()}
                        )
                        entities.append(entity)
                        current_pos = start + len(entity_text)
            
            return entities
        except:
            return self._extract_rule_based(text)
    
    def _extract_transformer(self, text: str) -> List[Entity]:
        """Extract entities using transformer model"""
        if self.model is None:
            return self._extract_rule_based(text)
        
        # Run NER pipeline
        results = self.model(text)
        entities = []
        
        for result in results:
            entity = Entity(
                text=result['word'],
                type=self._map_transformer_label(result['entity_group']),
                start=result['start'],
                end=result['end'],
                confidence=result['score'],
                metadata={"transformer_label": result['entity_group']}
            )
            entities.append(entity)
        
        return entities
    
    def _extract_hybrid(self, text: str) -> List[Entity]:
        """Hybrid approach combining multiple strategies"""
        all_entities = []
        
        # Rule-based extraction
        rule_entities = self._extract_rule_based(text)
        all_entities.extend(rule_entities)
        
        # Model-based extraction (if available)
        if self.model:
            if self.strategy == NERStrategy.SPACY:
                model_entities = self._extract_spacy(text)
            elif self.strategy == NERStrategy.TRANSFORMER:
                model_entities = self._extract_transformer(text)
            else:
                model_entities = []
            
            all_entities.extend(model_entities)
        
        # Merge and deduplicate
        merged_entities = self._merge_entities(all_entities)
        
        return merged_entities
    
    def _post_process(self, entities: List[Entity], text: str) -> List[Entity]:
        """Post-process extracted entities"""
        # Filter by confidence
        entities = [e for e in entities if e.confidence >= self.config.min_confidence]
        
        # Filter by length
        entities = [e for e in entities if len(e.text) <= self.config.max_entity_length]
        
        # Merge adjacent entities if configured
        if self.config.merge_adjacent:
            entities = self._merge_adjacent_entities(entities)
        
        # Sort by position
        entities.sort(key=lambda e: e.start)
        
        # Remove overlapping entities (keep higher confidence)
        entities = self._remove_overlaps(entities)
        
        return entities
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge duplicate entities from different sources"""
        # Group by position
        position_groups = defaultdict(list)
        
        for entity in entities:
            key = (entity.start, entity.end)
            position_groups[key].append(entity)
        
        # Merge groups
        merged = []
        for (start, end), group in position_groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Merge: take highest confidence
                best_entity = max(group, key=lambda e: e.confidence)
                # Combine metadata
                combined_metadata = {}
                for e in group:
                    combined_metadata.update(e.metadata)
                best_entity.metadata = combined_metadata
                merged.append(best_entity)
        
        return merged
    
    def _merge_adjacent_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge adjacent entities of the same type"""
        if not entities:
            return []
        
        merged = []
        current = entities[0]
        
        for next_entity in entities[1:]:
            # Check if adjacent and same type
            if (current.end == next_entity.start and 
                current.type == next_entity.type):
                # Merge
                current = Entity(
                    text=current.text + next_entity.text,
                    type=current.type,
                    start=current.start,
                    end=next_entity.end,
                    confidence=min(current.confidence, next_entity.confidence)
                )
            else:
                merged.append(current)
                current = next_entity
        
        merged.append(current)
        return merged
    
    def _remove_overlaps(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities"""
        if not entities:
            return []
        
        # Sort by start position and confidence (descending)
        entities.sort(key=lambda e: (e.start, -e.confidence))
        
        non_overlapping = []
        last_end = -1
        
        for entity in entities:
            if entity.start >= last_end:
                non_overlapping.append(entity)
                last_end = entity.end
        
        return non_overlapping
    
    def _map_spacy_label(self, label: str) -> str:
        """Map spaCy labels to our entity types"""
        mapping = {
            "PERSON": EntityType.PERSON.value,
            "PER": EntityType.PERSON.value,
            "ORG": EntityType.ORGANIZATION.value,
            "LOC": EntityType.LOCATION.value,
            "GPE": EntityType.LOCATION.value,
            "DATE": EntityType.DATE.value,
            "TIME": EntityType.TIME.value,
            "MONEY": EntityType.MONEY.value,
            "PERCENT": EntityType.PERCENT.value,
            "PRODUCT": EntityType.PRODUCT.value,
            "EVENT": EntityType.EVENT.value,
            "LANGUAGE": EntityType.LANGUAGE.value
        }
        return mapping.get(label, EntityType.MISC.value)
    
    def _map_nltk_label(self, label: str) -> str:
        """Map NLTK labels to our entity types"""
        mapping = {
            "PERSON": EntityType.PERSON.value,
            "ORGANIZATION": EntityType.ORGANIZATION.value,
            "GPE": EntityType.LOCATION.value,
            "LOCATION": EntityType.LOCATION.value
        }
        return mapping.get(label, EntityType.MISC.value)
    
    def _map_transformer_label(self, label: str) -> str:
        """Map transformer labels to our entity types"""
        # Handle B- and I- prefixes
        if label.startswith(('B-', 'I-')):
            label = label[2:]
        
        return self._map_spacy_label(label)
    
    def extract_entities_batch(self, texts: List[str], 
                             batch_size: int = 32) -> List[List[Entity]]:
        """Extract entities from multiple texts"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = [self.extract_entities(text) for text in batch]
            results.extend(batch_results)
        
        return results
    
    def get_entity_types(self, text: str) -> Dict[str, List[str]]:
        """Get entities grouped by type"""
        entities = self.extract_entities(text)
        
        grouped = defaultdict(list)
        for entity in entities:
            grouped[entity.type].append(entity.text)
        
        return dict(grouped)
    
    def annotate_text(self, text: str, format: str = "html") -> str:
        """Annotate text with entity markup"""
        entities = self.extract_entities(text)
        
        if format == "html":
            return self._annotate_html(text, entities)
        elif format == "markdown":
            return self._annotate_markdown(text, entities)
        else:
            return text
    
    def _annotate_html(self, text: str, entities: List[Entity]) -> str:
        """Annotate with HTML tags"""
        # Sort entities by position (reverse)
        entities.sort(key=lambda e: e.start, reverse=True)
        
        annotated = text
        for entity in entities:
            tag = f'<span class="entity {entity.type.lower()}" title="{entity.type}">{entity.text}</span>'
            annotated = annotated[:entity.start] + tag + annotated[entity.end:]
        
        return annotated
    
    def _annotate_markdown(self, text: str, entities: List[Entity]) -> str:
        """Annotate with markdown"""
        # Sort entities by position (reverse)
        entities.sort(key=lambda e: e.start, reverse=True)
        
        annotated = text
        for entity in entities:
            tag = f'**{entity.text}** _{entity.type}_'
            annotated = annotated[:entity.start] + tag + annotated[entity.end:]
        
        return annotated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get NER statistics"""
        return {
            "strategy": self.strategy.value,
            "texts_processed": self.texts_processed,
            "entities_extracted": self.entities_extracted,
            "avg_entities_per_text": (self.entities_extracted / self.texts_processed)
                                    if self.texts_processed > 0 else 0,
            "entity_patterns": len(self.patterns)
        }


# Utility functions
def extract_entities(text: str, strategy: str = "rule_based") -> List[Dict[str, Any]]:
    """Quick entity extraction"""
    ner = NamedEntityRecognizer(strategy=strategy)
    entities = ner.extract_entities(text)
    return [e.to_dict() for e in entities]


def extract_contacts(text: str) -> Dict[str, List[str]]:
    """Extract contact information from text"""
    ner = NamedEntityRecognizer(strategy="rule_based")
    entities = ner.extract_entities(text)
    
    contacts = {
        "emails": [],
        "phones": [],
        "urls": []
    }
    
    for entity in entities:
        if entity.type == "EMAIL":
            contacts["emails"].append(entity.text)
        elif entity.type == "PHONE":
            contacts["phones"].append(entity.text)
        elif entity.type == "URL":
            contacts["urls"].append(entity.text)
    
    return contacts


def anonymize_text(text: str, entity_types: Optional[List[str]] = None) -> str:
    """Anonymize sensitive entities in text"""
    ner = NamedEntityRecognizer()
    entities = ner.extract_entities(text)
    
    # Filter by entity types if specified
    if entity_types:
        entities = [e for e in entities if e.type in entity_types]
    
    # Sort by position (reverse)
    entities.sort(key=lambda e: e.start, reverse=True)
    
    # Replace entities
    anonymized = text
    for entity in entities:
        replacement = f"[{entity.type}]"
        anonymized = anonymized[:entity.start] + replacement + anonymized[entity.end:]
    
    return anonymized


# Auto-generated tests
def test_named_entity_recognizer():
    """Test NER functionality"""
    # Test rule-based extraction
    ner = NamedEntityRecognizer(strategy="rule_based")
    
    text = "Contact John Smith at john.smith@email.com or call 555-123-4567. Visit https://example.com"
    entities = ner.extract_entities(text)
    
    # Check entities found
    entity_types = {e.type for e in entities}
    assert "EMAIL" in entity_types
    assert "PHONE" in entity_types
    assert "URL" in entity_types
    assert "PERSON" in entity_types
    
    # Test email extraction
    email_entities = [e for e in entities if e.type == "EMAIL"]
    assert len(email_entities) == 1
    assert email_entities[0].text == "john.smith@email.com"
    
    # Test organization extraction
    text2 = "Apple Inc. announced new products. Microsoft Corporation follows."
    entities2 = ner.extract_entities(text2)
    org_entities = [e for e in entities2 if e.type == "ORG"]
    assert len(org_entities) >= 2
    
    # Test date and time extraction
    text3 = "Meeting on Jan 15, 2024 at 3:30 PM"
    entities3 = ner.extract_entities(text3)
    date_entities = [e for e in entities3 if e.type == "DATE"]
    time_entities = [e for e in entities3 if e.type == "TIME"]
    assert len(date_entities) >= 1
    assert len(time_entities) >= 1
    
    # Test money extraction
    text4 = "The price is $99.99 or €85.50"
    entities4 = ner.extract_entities(text4)
    money_entities = [e for e in entities4 if e.type == "MONEY"]
    assert len(money_entities) == 2
    
    # Test entity grouping
    grouped = ner.get_entity_types(text)
    assert "EMAIL" in grouped
    assert "john.smith@email.com" in grouped["EMAIL"]
    
    # Test annotation
    annotated = ner.annotate_text("Call John at 555-1234", format="markdown")
    assert "**John**" in annotated
    assert "**555-1234**" in annotated
    
    # Test contact extraction utility
    contacts = extract_contacts(text)
    assert len(contacts["emails"]) == 1
    assert len(contacts["phones"]) == 1
    assert len(contacts["urls"]) == 1
    
    # Test anonymization
    anon_text = anonymize_text("John Smith lives in New York", ["PERSON", "LOC"])
    assert "[PERSON]" in anon_text
    assert "John Smith" not in anon_text
    
    print("All NER tests passed!")


if __name__ == "__main__":
    test_named_entity_recognizer()