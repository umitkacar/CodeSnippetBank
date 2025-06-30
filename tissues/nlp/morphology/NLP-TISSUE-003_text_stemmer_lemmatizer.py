"""
Tissue ID: NLP-TISSUE-003
Title: Multi-Algorithm Text Stemmer and Lemmatizer
Category: nlp/morphology
Tags: ["stemming", "lemmatization", "text-normalization", "nlp", "morphology"]
Difficulty: Intermediate
Dependencies: ["nltk>=3.8"]
Performance: O(n) where n is number of tokens
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive text normalization tissue that provides both stemming and lemmatization
capabilities. Supports multiple algorithms (Porter, Snowball, Lancaster) and languages.
Includes part-of-speech aware lemmatization for better accuracy.

Use Cases:
- Text normalization for search engines
- Document similarity computation
- Information retrieval systems
- Chatbot intent matching
- Text mining and analytics

Example Usage:
    # Stemming
    stemmer = TextStemmer(algorithm="porter")
    stemmed = stemmer.stem_tokens(["running", "ran", "runs"])
    # Result: ["run", "ran", "run"]
    
    # Lemmatization
    lemmatizer = TextLemmatizer()
    lemmatized = lemmatizer.lemmatize_tokens(["better", "ran", "geese"])
    # Result: ["good", "run", "goose"]
    
    # Combined processor
    processor = MorphologicalProcessor()
    normalized = processor.normalize(tokens, method="lemmatize")
"""

from typing import List, Dict, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re


class StemmingAlgorithm(Enum):
    """Available stemming algorithms"""
    PORTER = "porter"
    SNOWBALL = "snowball"
    LANCASTER = "lancaster"
    REGEX = "regex"


class PartOfSpeech(Enum):
    """Part of speech tags for lemmatization"""
    NOUN = "n"
    VERB = "v"
    ADJECTIVE = "a"
    ADVERB = "r"
    
    @classmethod
    def from_tag(cls, tag: str) -> 'PartOfSpeech':
        """Convert from Penn Treebank tags"""
        tag = tag.upper()
        if tag.startswith('N'):
            return cls.NOUN
        elif tag.startswith('V'):
            return cls.VERB
        elif tag.startswith('J'):
            return cls.ADJECTIVE
        elif tag.startswith('R'):
            return cls.ADVERB
        else:
            return cls.NOUN  # Default


@dataclass
class MorphologyConfig:
    """Configuration for morphological processing"""
    lowercase: bool = True
    handle_contractions: bool = True
    preserve_case_information: bool = False
    min_word_length: int = 2
    custom_rules: Dict[str, str] = field(default_factory=dict)
    exceptions: Set[str] = field(default_factory=set)


class TextStemmer:
    """
    Multi-algorithm text stemmer.
    Tissue Type: FUNCTIONAL - Core text normalization.
    """
    
    # Common suffixes for simple regex stemmer
    COMMON_SUFFIXES = [
        'ing', 'ed', 'es', 's', 'er', 'est', 'ly', 'ness',
        'ment', 'ful', 'less', 'ize', 'ise', 'able', 'ible'
    ]
    
    def __init__(self,
                 algorithm: str = "porter",
                 language: str = "english",
                 config: Optional[MorphologyConfig] = None):
        """
        Initialize stemmer.
        
        Args:
            algorithm: Stemming algorithm to use
            language: Language for stemming
            config: Configuration options
        """
        self.algorithm = StemmingAlgorithm(algorithm.lower())
        self.language = language.lower()
        self.config = config or MorphologyConfig()
        
        # Initialize stemmers
        self._init_stemmers()
        
        # Statistics
        self.words_processed = 0
        self.stems_created = 0
    
    def _init_stemmers(self):
        """Initialize stemming algorithms"""
        self.stemmers = {}
        
        try:
            import nltk
            
            # Porter Stemmer
            from nltk.stem import PorterStemmer
            self.stemmers[StemmingAlgorithm.PORTER] = PorterStemmer()
            
            # Snowball Stemmer
            from nltk.stem import SnowballStemmer
            if self.language in SnowballStemmer.languages:
                self.stemmers[StemmingAlgorithm.SNOWBALL] = SnowballStemmer(self.language)
            
            # Lancaster Stemmer (English only)
            if self.language == "english":
                from nltk.stem import LancasterStemmer
                self.stemmers[StemmingAlgorithm.LANCASTER] = LancasterStemmer()
        except ImportError:
            print("Warning: NLTK not available. Using regex stemmer only.")
        
        # Always have regex stemmer as fallback
        self.stemmers[StemmingAlgorithm.REGEX] = self._regex_stemmer
    
    def stem(self, word: str) -> str:
        """Stem a single word"""
        if not word or len(word) < self.config.min_word_length:
            return word
        
        # Check exceptions
        if word.lower() in self.config.exceptions:
            return word
        
        # Check custom rules
        if word.lower() in self.config.custom_rules:
            return self.config.custom_rules[word.lower()]
        
        # Apply lowercase if configured
        original_word = word
        if self.config.lowercase:
            word = word.lower()
        
        # Get stemmer
        if self.algorithm in self.stemmers:
            stemmer = self.stemmers[self.algorithm]
            if callable(stemmer):
                stem = stemmer(word)
            else:
                stem = stemmer.stem(word)
        else:
            # Fallback to regex
            stem = self._regex_stemmer(word)
        
        # Preserve case if needed
        if self.config.preserve_case_information and not self.config.lowercase:
            stem = self._preserve_case(stem, original_word)
        
        self.words_processed += 1
        if stem != word:
            self.stems_created += 1
        
        return stem
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Stem a list of tokens"""
        return [self.stem(token) for token in tokens]
    
    def _regex_stemmer(self, word: str) -> str:
        """Simple regex-based stemmer"""
        # Sort suffixes by length (longest first)
        for suffix in sorted(self.COMMON_SUFFIXES, key=len, reverse=True):
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        return word
    
    def _preserve_case(self, stem: str, original: str) -> str:
        """Preserve original case pattern"""
        if original.isupper():
            return stem.upper()
        elif original[0].isupper():
            return stem.capitalize()
        return stem
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get stemming statistics"""
        return {
            "algorithm": self.algorithm.value,
            "language": self.language,
            "words_processed": self.words_processed,
            "stems_created": self.stems_created,
            "stem_ratio": (self.stems_created / self.words_processed * 100)
                         if self.words_processed > 0 else 0
        }


class TextLemmatizer:
    """
    Part-of-speech aware lemmatizer.
    Tissue Type: FUNCTIONAL - Advanced text normalization.
    """
    
    # Common irregular forms
    IRREGULAR_FORMS = {
        "better": ("good", PartOfSpeech.ADJECTIVE),
        "best": ("good", PartOfSpeech.ADJECTIVE),
        "worse": ("bad", PartOfSpeech.ADJECTIVE),
        "worst": ("bad", PartOfSpeech.ADJECTIVE),
        "farther": ("far", PartOfSpeech.ADJECTIVE),
        "further": ("far", PartOfSpeech.ADJECTIVE),
        "elder": ("old", PartOfSpeech.ADJECTIVE),
        "eldest": ("old", PartOfSpeech.ADJECTIVE),
        "children": ("child", PartOfSpeech.NOUN),
        "geese": ("goose", PartOfSpeech.NOUN),
        "men": ("man", PartOfSpeech.NOUN),
        "women": ("woman", PartOfSpeech.NOUN),
        "teeth": ("tooth", PartOfSpeech.NOUN),
        "feet": ("foot", PartOfSpeech.NOUN),
        "mice": ("mouse", PartOfSpeech.NOUN),
        "went": ("go", PartOfSpeech.VERB),
        "gone": ("go", PartOfSpeech.VERB),
        "was": ("be", PartOfSpeech.VERB),
        "were": ("be", PartOfSpeech.VERB),
        "been": ("be", PartOfSpeech.VERB),
        "did": ("do", PartOfSpeech.VERB),
        "done": ("do", PartOfSpeech.VERB),
        "had": ("have", PartOfSpeech.VERB),
        "made": ("make", PartOfSpeech.VERB),
        "took": ("take", PartOfSpeech.VERB),
        "taken": ("take", PartOfSpeech.VERB),
        "came": ("come", PartOfSpeech.VERB),
        "saw": ("see", PartOfSpeech.VERB),
        "seen": ("see", PartOfSpeech.VERB)
    }
    
    def __init__(self,
                 language: str = "english",
                 config: Optional[MorphologyConfig] = None,
                 use_pos_tags: bool = True):
        """
        Initialize lemmatizer.
        
        Args:
            language: Language for lemmatization
            config: Configuration options
            use_pos_tags: Whether to use POS tags for better accuracy
        """
        self.language = language.lower()
        self.config = config or MorphologyConfig()
        self.use_pos_tags = use_pos_tags
        
        # Initialize lemmatizer
        self._init_lemmatizer()
        
        # Statistics
        self.words_processed = 0
        self.lemmas_created = 0
    
    def _init_lemmatizer(self):
        """Initialize lemmatization engine"""
        self.lemmatizer = None
        
        try:
            import nltk
            from nltk.stem import WordNetLemmatizer
            
            # Download required data
            try:
                nltk.data.find('wordnet')
            except:
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
            
            self.lemmatizer = WordNetLemmatizer()
            
            # POS tagger for better lemmatization
            if self.use_pos_tags:
                self.pos_tagger = nltk.pos_tag
        except ImportError:
            print("Warning: NLTK not available. Using rule-based lemmatizer.")
    
    def lemmatize(self, word: str, pos: Optional[PartOfSpeech] = None) -> str:
        """Lemmatize a single word"""
        if not word or len(word) < self.config.min_word_length:
            return word
        
        # Check exceptions
        if word.lower() in self.config.exceptions:
            return word
        
        # Check custom rules
        if word.lower() in self.config.custom_rules:
            return self.config.custom_rules[word.lower()]
        
        # Check irregular forms
        if word.lower() in self.IRREGULAR_FORMS:
            lemma, expected_pos = self.IRREGULAR_FORMS[word.lower()]
            if pos is None or pos == expected_pos:
                return lemma
        
        # Apply lowercase if configured
        original_word = word
        if self.config.lowercase:
            word = word.lower()
        
        # Lemmatize
        if self.lemmatizer:
            if pos:
                lemma = self.lemmatizer.lemmatize(word, pos=pos.value)
            else:
                # Try all POS tags and take shortest result
                candidates = []
                for p in PartOfSpeech:
                    candidates.append(self.lemmatizer.lemmatize(word, pos=p.value))
                lemma = min(candidates, key=len)
        else:
            # Fallback to rule-based
            lemma = self._rule_based_lemmatize(word, pos)
        
        # Preserve case if needed
        if self.config.preserve_case_information and not self.config.lowercase:
            lemma = self._preserve_case(lemma, original_word)
        
        self.words_processed += 1
        if lemma != word:
            self.lemmas_created += 1
        
        return lemma
    
    def lemmatize_tokens(self, tokens: List[str], 
                        pos_tags: Optional[List[str]] = None) -> List[str]:
        """Lemmatize a list of tokens"""
        if self.use_pos_tags and pos_tags is None and self.lemmatizer:
            # Get POS tags
            try:
                tagged = self.pos_tagger(tokens)
                pos_tags = [tag for _, tag in tagged]
            except:
                pos_tags = None
        
        lemmas = []
        for i, token in enumerate(tokens):
            if pos_tags and i < len(pos_tags):
                pos = PartOfSpeech.from_tag(pos_tags[i])
            else:
                pos = None
            lemmas.append(self.lemmatize(token, pos))
        
        return lemmas
    
    def _rule_based_lemmatize(self, word: str, pos: Optional[PartOfSpeech]) -> str:
        """Simple rule-based lemmatization"""
        # Noun rules
        if pos is None or pos == PartOfSpeech.NOUN:
            if word.endswith('ies') and len(word) > 4:
                return word[:-3] + 'y'
            elif word.endswith('es') and len(word) > 3:
                if word[-3] in 'sxz' or word.endswith('sh') or word.endswith('ch'):
                    return word[:-2]
            elif word.endswith('s') and len(word) > 2 and word[-2] not in 'su':
                return word[:-1]
        
        # Verb rules
        if pos is None or pos == PartOfSpeech.VERB:
            if word.endswith('ed') and len(word) > 3:
                if word[-3] == word[-4]:  # doubled consonant
                    return word[:-3]
                else:
                    return word[:-2]
            elif word.endswith('ing') and len(word) > 4:
                if word[-4] == word[-5]:  # doubled consonant
                    return word[:-4]
                else:
                    return word[:-3]
        
        # Adjective rules
        if pos is None or pos == PartOfSpeech.ADJECTIVE:
            if word.endswith('er') and len(word) > 3:
                return word[:-2]
            elif word.endswith('est') and len(word) > 4:
                return word[:-3]
        
        return word
    
    def _preserve_case(self, lemma: str, original: str) -> str:
        """Preserve original case pattern"""
        if original.isupper():
            return lemma.upper()
        elif original[0].isupper():
            return lemma.capitalize()
        return lemma
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get lemmatization statistics"""
        return {
            "language": self.language,
            "use_pos_tags": self.use_pos_tags,
            "words_processed": self.words_processed,
            "lemmas_created": self.lemmas_created,
            "lemma_ratio": (self.lemmas_created / self.words_processed * 100)
                          if self.words_processed > 0 else 0
        }


class MorphologicalProcessor:
    """
    Combined morphological processor with both stemming and lemmatization.
    Tissue Type: FUNCTIONAL - Comprehensive text normalization.
    """
    
    def __init__(self,
                 default_method: str = "lemmatize",
                 language: str = "english",
                 config: Optional[MorphologyConfig] = None):
        """
        Initialize morphological processor.
        
        Args:
            default_method: Default normalization method
            language: Language for processing
            config: Configuration options
        """
        self.default_method = default_method
        self.language = language
        self.config = config or MorphologyConfig()
        
        # Initialize processors
        self.stemmer = TextStemmer(language=language, config=config)
        self.lemmatizer = TextLemmatizer(language=language, config=config)
        
        # Handle contractions
        self.contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
    
    def normalize(self, tokens: List[str], 
                 method: Optional[str] = None,
                 pos_tags: Optional[List[str]] = None) -> List[str]:
        """
        Normalize tokens using specified method.
        
        Args:
            tokens: List of tokens to normalize
            method: 'stem', 'lemmatize', or 'both'
            pos_tags: Optional POS tags for lemmatization
            
        Returns:
            Normalized tokens
        """
        method = method or self.default_method
        
        # Handle contractions first
        if self.config.handle_contractions:
            tokens = self._expand_contractions(tokens)
        
        if method == "stem":
            return self.stemmer.stem_tokens(tokens)
        elif method == "lemmatize":
            return self.lemmatizer.lemmatize_tokens(tokens, pos_tags)
        elif method == "both":
            # Lemmatize first, then stem
            lemmas = self.lemmatizer.lemmatize_tokens(tokens, pos_tags)
            return self.stemmer.stem_tokens(lemmas)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _expand_contractions(self, tokens: List[str]) -> List[str]:
        """Expand contractions in tokens"""
        expanded = []
        for token in tokens:
            lower_token = token.lower()
            
            # Check full contractions
            if lower_token in self.contractions:
                expansion = self.contractions[lower_token].split()
                # Preserve case
                if token[0].isupper():
                    expansion[0] = expansion[0].capitalize()
                expanded.extend(expansion)
            else:
                # Check suffixes
                for suffix, expansion in self.contractions.items():
                    if lower_token.endswith(suffix):
                        base = token[:-len(suffix)]
                        expanded.append(base)
                        expanded.extend(expansion.strip().split())
                        break
                else:
                    expanded.append(token)
        
        return expanded
    
    def compare_methods(self, tokens: List[str]) -> Dict[str, List[str]]:
        """Compare different normalization methods"""
        return {
            "original": tokens,
            "stemmed": self.stemmer.stem_tokens(tokens),
            "lemmatized": self.lemmatizer.lemmatize_tokens(tokens),
            "both": self.normalize(tokens, method="both")
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get combined statistics"""
        return {
            "stemmer_stats": self.stemmer.get_statistics(),
            "lemmatizer_stats": self.lemmatizer.get_statistics(),
            "default_method": self.default_method,
            "language": self.language
        }


# Utility functions
def stem_text(text: str, algorithm: str = "porter") -> str:
    """Quick stemming of text"""
    stemmer = TextStemmer(algorithm=algorithm)
    tokens = text.split()
    stemmed = stemmer.stem_tokens(tokens)
    return ' '.join(stemmed)


def lemmatize_text(text: str, use_pos: bool = True) -> str:
    """Quick lemmatization of text"""
    lemmatizer = TextLemmatizer(use_pos_tags=use_pos)
    tokens = text.split()
    lemmatized = lemmatizer.lemmatize_tokens(tokens)
    return ' '.join(lemmatized)


def normalize_for_search(text: str) -> str:
    """Normalize text for search applications"""
    processor = MorphologicalProcessor(
        config=MorphologyConfig(
            lowercase=True,
            handle_contractions=True,
            min_word_length=2
        )
    )
    tokens = text.split()
    normalized = processor.normalize(tokens, method="lemmatize")
    return ' '.join(normalized)


# Auto-generated tests
def test_morphological_processing():
    """Test morphological processing functionality"""
    # Test stemming
    stemmer = TextStemmer(algorithm="porter")
    
    test_words = ["running", "runs", "ran", "runner", "easily", "fairly"]
    stemmed = stemmer.stem_tokens(test_words)
    assert len(stemmed) == len(test_words)
    assert stemmed[0] == stemmed[1]  # running and runs should have same stem
    
    # Test lemmatization
    lemmatizer = TextLemmatizer()
    
    test_words = ["better", "ran", "geese", "children", "quickly"]
    lemmatized = lemmatizer.lemmatize_tokens(test_words)
    assert "good" in lemmatized or "well" in lemmatized  # better -> good/well
    assert "goose" in lemmatized  # geese -> goose
    assert "child" in lemmatized  # children -> child
    
    # Test combined processor
    processor = MorphologicalProcessor()
    
    test_tokens = ["I'm", "running", "quickly", "to", "the", "stores"]
    normalized = processor.normalize(test_tokens)
    assert len(normalized) > len(test_tokens)  # Contractions expanded
    
    # Test comparison
    comparison = processor.compare_methods(["running", "better", "children"])
    assert "stemmed" in comparison
    assert "lemmatized" in comparison
    assert len(comparison["original"]) == len(comparison["stemmed"])
    
    # Test statistics
    stats = processor.get_statistics()
    assert "stemmer_stats" in stats
    assert "lemmatizer_stats" in stats
    
    print("All morphological processing tests passed!")


if __name__ == "__main__":
    test_morphological_processing()