"""
Tissue ID: NLP-TISSUE-002
Title: Multi-Language Stop Words Remover
Category: nlp/preprocessing
Tags: ["stop-words", "text-cleaning", "nlp", "preprocessing", "multi-language"]
Difficulty: Beginner
Dependencies: ["nltk>=3.8"]
Performance: O(n) where n is number of tokens
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
An intelligent stop words removal tissue that supports multiple languages and
custom stop word lists. Provides context-aware removal with options to preserve
important stop words based on the task (e.g., keeping "not" for sentiment analysis).

Use Cases:
- Text preprocessing for ML models
- Document summarization
- Keyword extraction
- Search query optimization
- Content analysis

Example Usage:
    remover = StopWordsRemover(language="en")
    
    # Basic removal
    tokens = ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
    cleaned = remover.remove(tokens)
    # Result: ["quick", "brown", "fox", "jumps", "lazy", "dog"]
    
    # Context-aware removal
    cleaned = remover.remove(tokens, preserve_negations=True)
    
    # With custom stop words
    remover.add_stop_words(["quick", "lazy"])
    cleaned = remover.remove(tokens)
"""

from typing import List, Set, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
import json
import os
from pathlib import Path


@dataclass
class StopWordsConfig:
    """Configuration for stop words removal"""
    case_sensitive: bool = False
    preserve_negations: bool = False
    preserve_questions: bool = False
    preserve_pronouns: bool = False
    min_word_length: int = 0
    max_word_length: Optional[int] = None
    preserve_numbers: bool = True
    custom_preserve: Set[str] = field(default_factory=set)


class StopWordsRemover:
    """
    Multi-language stop words remover with context awareness.
    Tissue Type: FUNCTIONAL - Core text preprocessing functionality.
    """
    
    # Default stop words for major languages
    DEFAULT_STOP_WORDS = {
        "en": {
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
            "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
            "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
            "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
            "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
            "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
            "at", "by", "for", "with", "about", "against", "between", "into", "through",
            "during", "before", "after", "above", "below", "to", "from", "up", "down",
            "in", "out", "on", "off", "over", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "can", "will", "just",
            "should", "now"
        },
        "es": {
            "el", "la", "de", "que", "y", "a", "en", "un", "ser", "se", "no", "haber",
            "por", "con", "su", "para", "como", "estar", "tener", "le", "lo", "todo",
            "pero", "más", "hacer", "o", "poder", "decir", "este", "ir", "otro",
            "ese", "si", "me", "ya", "ver", "porque", "dar", "cuando", "muy",
            "sin", "vez", "mucho", "saber", "qué", "sobre", "mi", "alguno", "mismo",
            "también", "hasta", "año", "dos", "querer", "entre", "así", "primero",
            "desde", "grande", "eso", "ni", "nos", "llegar", "pasar", "tiempo", "ella",
            "sí", "día", "uno", "bien", "poco", "deber", "entonces", "poner", "cosa",
            "tanto", "hombre", "parecer", "nuestro", "tan", "donde", "ahora", "parte",
            "después", "vida", "quedar", "siempre", "creer", "hablar", "llevar",
            "dejar", "nada", "cada", "seguir", "menos", "nuevo", "encontrar"
        },
        "fr": {
            "le", "de", "un", "être", "et", "à", "il", "avoir", "ne", "je", "son",
            "que", "se", "qui", "ce", "dans", "en", "du", "elle", "au", "pour",
            "pas", "vous", "par", "sur", "faire", "plus", "dire", "me", "on", "mon",
            "lui", "nous", "comme", "mais", "pouvoir", "avec", "tout", "y", "aller",
            "voir", "bien", "où", "sans", "tu", "ou", "leur", "homme", "si", "deux",
            "mari", "moi", "vouloir", "te", "femme", "venir", "quand", "grand",
            "celui", "si", "notre", "devoir", "là", "jour", "prendre", "même",
            "votre", "tout", "rien", "petit", "encore", "aussi", "quelque", "dont",
            "tout", "mer", "trouver", "donner", "temps", "ça", "peu", "même",
            "falloir", "sous", "parler", "alors", "main", "chose", "ton", "mettre",
            "vie", "savoir", "yeux", "passer", "après"
        },
        "de": {
            "der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich",
            "des", "auf", "für", "ist", "im", "dem", "nicht", "ein", "eine", "als",
            "auch", "es", "an", "werden", "aus", "er", "hat", "dass", "sie", "nach",
            "wird", "bei", "einer", "um", "am", "sind", "noch", "wie", "einem",
            "über", "einen", "so", "zum", "war", "haben", "nur", "oder", "aber",
            "vor", "zur", "bis", "mehr", "durch", "man", "sein", "wurde", "sei",
            "schon", "wenn", "habe", "seine", "ihre", "dann", "unter", "wir", "soll",
            "ich", "eines", "können", "ihm", "uns", "was", "ohne", "sowie", "zwischen",
            "können", "hatte", "gegen", "vom", "auch", "anderen", "anderen", "seit",
            "ja", "wurde", "jetzt", "immer", "seinen", "wohl", "dieses", "diesen",
            "wieder", "keine", "seiner", "worden"
        }
    }
    
    # Negation words to preserve in certain contexts
    NEGATION_WORDS = {
        "en": {"no", "not", "none", "nobody", "nothing", "neither", "never", "nor"},
        "es": {"no", "nunca", "jamás", "tampoco", "nadie", "ningún", "ninguna"},
        "fr": {"ne", "pas", "non", "jamais", "rien", "personne", "aucun", "aucune"},
        "de": {"nicht", "kein", "keine", "niemals", "niemand", "nichts"}
    }
    
    # Question words to preserve
    QUESTION_WORDS = {
        "en": {"what", "when", "where", "who", "whom", "whose", "which", "why", "how"},
        "es": {"qué", "cuándo", "dónde", "quién", "cuál", "por qué", "cómo"},
        "fr": {"quoi", "quand", "où", "qui", "quel", "quelle", "pourquoi", "comment"},
        "de": {"was", "wann", "wo", "wer", "welcher", "welche", "warum", "wie"}
    }
    
    def __init__(self,
                 language: str = "en",
                 config: Optional[StopWordsConfig] = None,
                 custom_stop_words: Optional[Set[str]] = None):
        """
        Initialize stop words remover.
        
        Args:
            language: Language code (en, es, fr, de, etc.)
            config: Configuration for removal behavior
            custom_stop_words: Additional stop words to use
        """
        self.language = language.lower()
        self.config = config or StopWordsConfig()
        
        # Initialize stop words
        self.stop_words = self._load_stop_words()
        if custom_stop_words:
            self.stop_words.update(custom_stop_words)
        
        # Statistics
        self.words_processed = 0
        self.words_removed = 0
    
    def _load_stop_words(self) -> Set[str]:
        """Load stop words for the specified language"""
        # Try to load from default dictionary
        if self.language in self.DEFAULT_STOP_WORDS:
            return set(self.DEFAULT_STOP_WORDS[self.language])
        
        # Try to load from NLTK if available
        try:
            import nltk
            from nltk.corpus import stopwords
            try:
                return set(stopwords.words(self.language))
            except:
                # Download if not available
                nltk.download('stopwords', quiet=True)
                return set(stopwords.words(self.language))
        except:
            pass
        
        # Fallback to English if language not found
        print(f"Warning: Stop words for '{self.language}' not found. Using English.")
        return set(self.DEFAULT_STOP_WORDS["en"])
    
    def remove(self, tokens: List[str], **kwargs) -> List[str]:
        """
        Remove stop words from token list.
        
        Args:
            tokens: List of tokens to process
            **kwargs: Override config options
            
        Returns:
            List of tokens with stop words removed
        """
        if not tokens:
            return []
        
        # Merge configuration
        config = self._merge_config(kwargs)
        
        # Get context-aware stop words
        effective_stop_words = self._get_effective_stop_words(tokens, config)
        
        # Filter tokens
        cleaned_tokens = []
        for token in tokens:
            self.words_processed += 1
            
            # Check token against stop words
            if self._should_remove(token, effective_stop_words, config):
                self.words_removed += 1
                continue
            
            cleaned_tokens.append(token)
        
        return cleaned_tokens
    
    def _get_effective_stop_words(self, tokens: List[str], 
                                 config: StopWordsConfig) -> Set[str]:
        """Get stop words considering context and configuration"""
        effective_stop_words = self.stop_words.copy()
        
        # Remove negations if preserving
        if config.preserve_negations:
            negations = self.NEGATION_WORDS.get(self.language, set())
            effective_stop_words -= negations
        
        # Remove question words if preserving
        if config.preserve_questions:
            questions = self.QUESTION_WORDS.get(self.language, set())
            effective_stop_words -= questions
        
        # Remove pronouns if preserving
        if config.preserve_pronouns:
            # Simple pronoun detection
            pronouns = {"i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"}
            effective_stop_words -= pronouns
        
        # Remove custom preserved words
        effective_stop_words -= config.custom_preserve
        
        return effective_stop_words
    
    def _should_remove(self, token: str, stop_words: Set[str], 
                      config: StopWordsConfig) -> bool:
        """Determine if token should be removed"""
        # Handle case sensitivity
        check_token = token.lower() if not config.case_sensitive else token
        
        # Check length constraints
        if len(token) < config.min_word_length:
            return True
        if config.max_word_length and len(token) > config.max_word_length:
            return True
        
        # Check if it's a number
        if not config.preserve_numbers and token.isdigit():
            return True
        
        # Check against stop words
        return check_token in stop_words
    
    def _merge_config(self, kwargs: Dict[str, Any]) -> StopWordsConfig:
        """Merge kwargs with default config"""
        return StopWordsConfig(
            case_sensitive=kwargs.get('case_sensitive', self.config.case_sensitive),
            preserve_negations=kwargs.get('preserve_negations', self.config.preserve_negations),
            preserve_questions=kwargs.get('preserve_questions', self.config.preserve_questions),
            preserve_pronouns=kwargs.get('preserve_pronouns', self.config.preserve_pronouns),
            min_word_length=kwargs.get('min_word_length', self.config.min_word_length),
            max_word_length=kwargs.get('max_word_length', self.config.max_word_length),
            preserve_numbers=kwargs.get('preserve_numbers', self.config.preserve_numbers),
            custom_preserve=kwargs.get('custom_preserve', self.config.custom_preserve)
        )
    
    def add_stop_words(self, words: Union[str, List[str], Set[str]]):
        """Add custom stop words"""
        if isinstance(words, str):
            words = [words]
        self.stop_words.update(words)
    
    def remove_stop_words(self, words: Union[str, List[str], Set[str]]):
        """Remove words from stop words list"""
        if isinstance(words, str):
            words = [words]
        self.stop_words -= set(words)
    
    def get_stop_words(self) -> Set[str]:
        """Get current stop words list"""
        return self.stop_words.copy()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze stop word distribution in text"""
        # Simple tokenization
        tokens = text.lower().split()
        total_words = len(tokens)
        
        stop_word_count = sum(1 for token in tokens if token in self.stop_words)
        unique_tokens = set(tokens)
        unique_stop_words = unique_tokens & self.stop_words
        
        return {
            "total_words": total_words,
            "stop_word_count": stop_word_count,
            "stop_word_percentage": (stop_word_count / total_words * 100) if total_words > 0 else 0,
            "unique_words": len(unique_tokens),
            "unique_stop_words": len(unique_stop_words),
            "most_common_stop_words": self._get_most_common(tokens, self.stop_words, 10)
        }
    
    def _get_most_common(self, tokens: List[str], filter_set: Set[str], n: int) -> List[Tuple[str, int]]:
        """Get most common tokens from a set"""
        counts = {}
        for token in tokens:
            if token in filter_set:
                counts[token] = counts.get(token, 0) + 1
        
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get removal statistics"""
        return {
            "language": self.language,
            "stop_words_count": len(self.stop_words),
            "words_processed": self.words_processed,
            "words_removed": self.words_removed,
            "removal_rate": (self.words_removed / self.words_processed * 100) 
                          if self.words_processed > 0 else 0
        }
    
    def export_stop_words(self, file_path: str):
        """Export stop words to file"""
        data = {
            "language": self.language,
            "stop_words": sorted(list(self.stop_words)),
            "count": len(self.stop_words)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                # Plain text, one word per line
                f.write('\n'.join(sorted(self.stop_words)))
    
    def import_stop_words(self, file_path: str, replace: bool = False):
        """Import stop words from file"""
        if replace:
            self.stop_words.clear()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                data = json.load(f)
                words = data.get('stop_words', [])
            else:
                words = [line.strip() for line in f if line.strip()]
        
        self.stop_words.update(words)


# Utility functions
def remove_stop_words(tokens: List[str], language: str = "en", **kwargs) -> List[str]:
    """Quick stop word removal"""
    remover = StopWordsRemover(language=language)
    return remover.remove(tokens, **kwargs)


def remove_stop_words_multiple_languages(tokens: List[str], 
                                        languages: List[str]) -> List[str]:
    """Remove stop words from multiple languages"""
    all_stop_words = set()
    for lang in languages:
        remover = StopWordsRemover(language=lang)
        all_stop_words.update(remover.get_stop_words())
    
    # Create remover with combined stop words
    remover = StopWordsRemover(custom_stop_words=all_stop_words)
    return remover.remove(tokens)


def analyze_stop_word_impact(text: str, language: str = "en") -> Dict[str, Any]:
    """Analyze the impact of stop word removal on text"""
    remover = StopWordsRemover(language=language)
    analysis = remover.analyze_text(text)
    
    # Add removal impact
    tokens = text.split()
    cleaned = remover.remove(tokens)
    
    analysis["tokens_before"] = len(tokens)
    analysis["tokens_after"] = len(cleaned)
    analysis["reduction_percentage"] = (
        (len(tokens) - len(cleaned)) / len(tokens) * 100 
        if tokens else 0
    )
    
    return analysis


# Auto-generated tests
def test_stop_words_remover():
    """Test stop words removal functionality"""
    # Test basic removal
    remover = StopWordsRemover(language="en")
    
    tokens = ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
    cleaned = remover.remove(tokens)
    assert "the" not in cleaned
    assert "quick" in cleaned
    assert "brown" in cleaned
    
    # Test case sensitivity
    tokens_mixed = ["The", "Quick", "Brown", "Fox"]
    cleaned = remover.remove(tokens_mixed)
    assert "The" not in cleaned  # Default is case insensitive
    
    cleaned_sensitive = remover.remove(tokens_mixed, case_sensitive=True)
    assert "The" in cleaned_sensitive  # "The" != "the"
    
    # Test negation preservation
    tokens_neg = ["I", "do", "not", "like", "this"]
    cleaned = remover.remove(tokens_neg, preserve_negations=True)
    assert "not" in cleaned
    assert "do" not in cleaned
    
    # Test custom stop words
    remover.add_stop_words(["quick", "lazy"])
    cleaned = remover.remove(tokens)
    assert "quick" not in cleaned
    assert "lazy" not in cleaned
    
    # Test statistics
    stats = remover.get_statistics()
    assert stats["words_processed"] > 0
    assert stats["words_removed"] > 0
    
    # Test analysis
    text = "The quick brown fox jumps over the lazy dog"
    analysis = remover.analyze_text(text)
    assert analysis["stop_word_percentage"] > 0
    
    print("All stop words removal tests passed!")


if __name__ == "__main__":
    test_stop_words_remover()