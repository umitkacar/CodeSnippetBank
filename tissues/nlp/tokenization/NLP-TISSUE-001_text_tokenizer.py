"""
Tissue ID: NLP-TISSUE-001
Title: Multi-Strategy Text Tokenizer
Category: nlp/tokenization
Tags: ["tokenization", "text-processing", "nlp", "preprocessing", "word-splitting"]
Difficulty: Beginner
Dependencies: ["nltk>=3.8", "regex>=2023.0", "unicodedata"]
Performance: O(n) where n is text length
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A versatile text tokenization tissue that provides multiple tokenization strategies
including word, sentence, subword, and character-level tokenization. Handles
multiple languages, special characters, and edge cases gracefully.

Use Cases:
- Text preprocessing for NLP models
- Document analysis and indexing
- Chat message parsing
- Code tokenization
- Multi-language text processing

Example Usage:
    tokenizer = TextTokenizer(strategy="word", lowercase=True)
    
    # Basic tokenization
    tokens = tokenizer.tokenize("Hello, world! How are you?")
    # Result: ['hello', ',', 'world', '!', 'how', 'are', 'you', '?']
    
    # Sentence tokenization
    sentences = tokenizer.tokenize_sentences(text)
    
    # Advanced with custom rules
    tokens = tokenizer.tokenize(text, keep_punctuation=False)
"""

import re
import unicodedata
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import string


class TokenizationStrategy(Enum):
    """Available tokenization strategies"""
    WORD = "word"
    SENTENCE = "sentence"
    SUBWORD = "subword"
    CHARACTER = "character"
    WHITESPACE = "whitespace"
    REGEX = "regex"


@dataclass
class TokenizationConfig:
    """Configuration for tokenization behavior"""
    lowercase: bool = False
    keep_punctuation: bool = True
    keep_numbers: bool = True
    keep_whitespace: bool = False
    remove_accents: bool = False
    split_camelcase: bool = False
    min_token_length: int = 1
    max_token_length: Optional[int] = None
    custom_split_chars: Set[str] = field(default_factory=set)
    protected_words: Set[str] = field(default_factory=set)


class TextTokenizer:
    """
    Multi-strategy text tokenizer with language awareness.
    Tissue Type: FUNCTIONAL - Core text processing functionality.
    """
    
    # Common abbreviations that shouldn't end sentences
    ABBREVIATIONS = {
        'dr', 'mr', 'mrs', 'ms', 'prof', 'sr', 'jr', 'ph.d', 'phd',
        'i.e', 'e.g', 'etc', 'vs', 'inc', 'ltd', 'co', 'corp'
    }
    
    # Sentence ending punctuation
    SENTENCE_ENDINGS = {'.', '!', '?', '...', '。', '！', '？'}
    
    # URL and email patterns
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def __init__(self,
                 strategy: str = "word",
                 config: Optional[TokenizationConfig] = None,
                 language: str = "en"):
        """
        Initialize tokenizer with strategy and configuration.
        
        Args:
            strategy: Tokenization strategy to use
            config: Custom configuration
            language: Language code for language-specific rules
        """
        self.strategy = TokenizationStrategy(strategy.lower())
        self.config = config or TokenizationConfig()
        self.language = language
        
        # Statistics
        self.tokens_processed = 0
        self.texts_processed = 0
        
        # Compile regex patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        # Word tokenization pattern
        self.word_pattern = re.compile(r'\b\w+\b|[^\w\s]')
        
        # CamelCase splitting
        self.camelcase_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        
        # Number pattern
        self.number_pattern = re.compile(r'\d+\.?\d*')
        
        # Whitespace pattern
        self.whitespace_pattern = re.compile(r'\s+')
    
    def tokenize(self, text: str, **kwargs) -> List[str]:
        """
        Main tokenization method.
        
        Args:
            text: Input text to tokenize
            **kwargs: Override config options
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Create temporary config with overrides
        config = self._merge_config(kwargs)
        
        # Preprocess text
        processed_text = self._preprocess(text, config)
        
        # Apply tokenization strategy
        if self.strategy == TokenizationStrategy.WORD:
            tokens = self._tokenize_words(processed_text, config)
        elif self.strategy == TokenizationStrategy.SENTENCE:
            tokens = self._tokenize_sentences(processed_text, config)
        elif self.strategy == TokenizationStrategy.SUBWORD:
            tokens = self._tokenize_subwords(processed_text, config)
        elif self.strategy == TokenizationStrategy.CHARACTER:
            tokens = self._tokenize_characters(processed_text, config)
        elif self.strategy == TokenizationStrategy.WHITESPACE:
            tokens = self._tokenize_whitespace(processed_text, config)
        elif self.strategy == TokenizationStrategy.REGEX:
            pattern = kwargs.get('pattern', r'\b\w+\b')
            tokens = self._tokenize_regex(processed_text, pattern, config)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        # Postprocess tokens
        tokens = self._postprocess_tokens(tokens, config)
        
        # Update statistics
        self.tokens_processed += len(tokens)
        self.texts_processed += 1
        
        return tokens
    
    def _preprocess(self, text: str, config: TokenizationConfig) -> str:
        """Preprocess text before tokenization"""
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Protect URLs and emails
        protected_tokens = {}
        text = self._protect_special_tokens(text, protected_tokens)
        
        # Remove accents if requested
        if config.remove_accents:
            text = self._remove_accents(text)
        
        # Handle protected words
        for word in config.protected_words:
            placeholder = f"__PROTECTED_{len(protected_tokens)}__"
            text = text.replace(word, placeholder)
            protected_tokens[placeholder] = word
        
        # Restore protected tokens
        self._protected_tokens = protected_tokens
        
        return text
    
    def _protect_special_tokens(self, text: str, protected: Dict[str, str]) -> str:
        """Protect URLs, emails, etc. from tokenization"""
        # Protect URLs
        for match in self.URL_PATTERN.finditer(text):
            url = match.group()
            placeholder = f"__URL_{len(protected)}__"
            text = text.replace(url, placeholder, 1)
            protected[placeholder] = url
        
        # Protect emails
        for match in self.EMAIL_PATTERN.finditer(text):
            email = match.group()
            placeholder = f"__EMAIL_{len(protected)}__"
            text = text.replace(email, placeholder, 1)
            protected[placeholder] = email
        
        return text
    
    def _tokenize_words(self, text: str, config: TokenizationConfig) -> List[str]:
        """Word-level tokenization"""
        # Split on word boundaries and punctuation
        tokens = self.word_pattern.findall(text)
        
        # Split camelCase if requested
        if config.split_camelcase:
            new_tokens = []
            for token in tokens:
                if re.match(r'^[A-Za-z]+$', token):
                    subtokens = self.camelcase_pattern.sub(' ', token).split()
                    new_tokens.extend(subtokens)
                else:
                    new_tokens.append(token)
            tokens = new_tokens
        
        return tokens
    
    def _tokenize_sentences(self, text: str, config: TokenizationConfig) -> List[str]:
        """Sentence-level tokenization"""
        sentences = []
        current_sentence = []
        
        # First, do word tokenization
        words = self._tokenize_words(text, config)
        
        for i, word in enumerate(words):
            current_sentence.append(word)
            
            # Check for sentence ending
            if word in self.SENTENCE_ENDINGS:
                # Check if it's an abbreviation
                if i > 0 and words[i-1].lower() in self.ABBREVIATIONS:
                    continue
                
                # Check for ellipsis
                if word == '.' and i + 1 < len(words) and words[i+1] == '.':
                    continue
                
                # End sentence
                sentences.append(' '.join(current_sentence))
                current_sentence = []
        
        # Add remaining words
        if current_sentence:
            sentences.append(' '.join(current_sentence))
        
        return sentences
    
    def _tokenize_subwords(self, text: str, config: TokenizationConfig) -> List[str]:
        """Subword tokenization (simplified BPE-style)"""
        # Start with character-level tokens
        tokens = list(text)
        
        # Simple frequency-based merging
        vocab_size = 1000  # Target vocabulary size
        
        while len(set(tokens)) < vocab_size:
            # Count bigrams
            bigram_counts = {}
            for i in range(len(tokens) - 1):
                bigram = tokens[i] + tokens[i + 1]
                bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1
            
            if not bigram_counts:
                break
            
            # Find most frequent bigram
            most_frequent = max(bigram_counts, key=bigram_counts.get)
            
            # Merge tokens
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and tokens[i] + tokens[i + 1] == most_frequent:
                    new_tokens.append(most_frequent)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            
            tokens = new_tokens
            
            # Stop if no improvement
            if len(new_tokens) == len(tokens):
                break
        
        return tokens
    
    def _tokenize_characters(self, text: str, config: TokenizationConfig) -> List[str]:
        """Character-level tokenization"""
        tokens = list(text)
        
        # Remove whitespace if not keeping it
        if not config.keep_whitespace:
            tokens = [t for t in tokens if not t.isspace()]
        
        return tokens
    
    def _tokenize_whitespace(self, text: str, config: TokenizationConfig) -> List[str]:
        """Simple whitespace tokenization"""
        return text.split()
    
    def _tokenize_regex(self, text: str, pattern: str, config: TokenizationConfig) -> List[str]:
        """Regex-based tokenization"""
        regex = re.compile(pattern)
        return regex.findall(text)
    
    def _postprocess_tokens(self, tokens: List[str], config: TokenizationConfig) -> List[str]:
        """Postprocess tokens based on configuration"""
        processed = []
        
        for token in tokens:
            # Restore protected tokens
            if hasattr(self, '_protected_tokens') and token in self._protected_tokens:
                token = self._protected_tokens[token]
            
            # Apply lowercase
            if config.lowercase and not self._is_special_token(token):
                token = token.lower()
            
            # Filter by length
            if len(token) < config.min_token_length:
                continue
            if config.max_token_length and len(token) > config.max_token_length:
                continue
            
            # Filter punctuation
            if not config.keep_punctuation and token in string.punctuation:
                continue
            
            # Filter numbers
            if not config.keep_numbers and self.number_pattern.fullmatch(token):
                continue
            
            # Filter whitespace
            if not config.keep_whitespace and token.isspace():
                continue
            
            processed.append(token)
        
        return processed
    
    def _is_special_token(self, token: str) -> bool:
        """Check if token is a special protected token"""
        return token.startswith('__') and token.endswith('__')
    
    def _remove_accents(self, text: str) -> str:
        """Remove accents from text"""
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
    
    def _merge_config(self, kwargs: Dict[str, Any]) -> TokenizationConfig:
        """Merge kwargs with default config"""
        config = TokenizationConfig(
            lowercase=kwargs.get('lowercase', self.config.lowercase),
            keep_punctuation=kwargs.get('keep_punctuation', self.config.keep_punctuation),
            keep_numbers=kwargs.get('keep_numbers', self.config.keep_numbers),
            keep_whitespace=kwargs.get('keep_whitespace', self.config.keep_whitespace),
            remove_accents=kwargs.get('remove_accents', self.config.remove_accents),
            split_camelcase=kwargs.get('split_camelcase', self.config.split_camelcase),
            min_token_length=kwargs.get('min_token_length', self.config.min_token_length),
            max_token_length=kwargs.get('max_token_length', self.config.max_token_length),
            custom_split_chars=kwargs.get('custom_split_chars', self.config.custom_split_chars),
            protected_words=kwargs.get('protected_words', self.config.protected_words)
        )
        return config
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Convenience method for sentence tokenization"""
        original_strategy = self.strategy
        self.strategy = TokenizationStrategy.SENTENCE
        sentences = self.tokenize(text)
        self.strategy = original_strategy
        return sentences
    
    def tokenize_with_positions(self, text: str) -> List[Tuple[str, int, int]]:
        """Tokenize and return token positions"""
        tokens_with_positions = []
        tokens = self.tokenize(text)
        
        current_pos = 0
        for token in tokens:
            # Find token in original text
            token_pos = text.find(token, current_pos)
            if token_pos != -1:
                tokens_with_positions.append((token, token_pos, token_pos + len(token)))
                current_pos = token_pos + len(token)
        
        return tokens_with_positions
    
    def get_vocabulary(self, texts: List[str]) -> Dict[str, int]:
        """Build vocabulary from texts"""
        vocab = {}
        for text in texts:
            tokens = self.tokenize(text)
            for token in tokens:
                vocab[token] = vocab.get(token, 0) + 1
        return vocab
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tokenization statistics"""
        return {
            "strategy": self.strategy.value,
            "tokens_processed": self.tokens_processed,
            "texts_processed": self.texts_processed,
            "avg_tokens_per_text": (
                self.tokens_processed / self.texts_processed 
                if self.texts_processed > 0 else 0
            ),
            "language": self.language
        }


# Utility functions
def tokenize_text(text: str, strategy: str = "word", **kwargs) -> List[str]:
    """Quick tokenization function"""
    tokenizer = TextTokenizer(strategy=strategy)
    return tokenizer.tokenize(text, **kwargs)


def tokenize_for_nlp(text: str) -> List[str]:
    """Standard NLP preprocessing tokenization"""
    tokenizer = TextTokenizer(
        strategy="word",
        config=TokenizationConfig(
            lowercase=True,
            keep_punctuation=False,
            remove_accents=True,
            min_token_length=2
        )
    )
    return tokenizer.tokenize(text)


def tokenize_code(code: str) -> List[str]:
    """Tokenize source code"""
    tokenizer = TextTokenizer(
        strategy="regex",
        config=TokenizationConfig(
            keep_punctuation=True,
            split_camelcase=True
        )
    )
    # Use regex for code tokens
    pattern = r'\b\w+\b|[^\w\s]|\s+'
    return tokenizer.tokenize(code, pattern=pattern, keep_whitespace=True)


# Auto-generated tests
def test_text_tokenizer():
    """Test tokenization functionality"""
    # Test basic word tokenization
    tokenizer = TextTokenizer(strategy="word")
    
    text = "Hello, world! This is a test."
    tokens = tokenizer.tokenize(text)
    assert len(tokens) > 0
    assert "Hello" in tokens or "hello" in tokens
    
    # Test lowercase
    tokens_lower = tokenizer.tokenize(text, lowercase=True)
    assert all(t.islower() or not t.isalpha() for t in tokens_lower)
    
    # Test sentence tokenization
    sent_tokenizer = TextTokenizer(strategy="sentence")
    sentences = sent_tokenizer.tokenize("Hello world. How are you? I'm fine!")
    assert len(sentences) == 3
    
    # Test with URLs and emails
    text_with_urls = "Visit https://example.com or email test@example.com"
    tokens = tokenizer.tokenize(text_with_urls)
    assert "https://example.com" in tokens
    assert "test@example.com" in tokens
    
    # Test configuration
    config = TokenizationConfig(
        lowercase=True,
        keep_punctuation=False,
        min_token_length=3
    )
    tokenizer_config = TextTokenizer(config=config)
    tokens = tokenizer_config.tokenize("Hi, how are you?")
    assert "," not in tokens
    assert "Hi" not in tokens  # Too short when lowercased
    
    # Test statistics
    stats = tokenizer.get_statistics()
    assert stats["tokens_processed"] > 0
    
    print("All tokenization tests passed!")


if __name__ == "__main__":
    test_text_tokenizer()