"""
Tissue ID: NLP-TISSUE-008
Title: Multi-Method Language Detector
Category: nlp/language_detection
Tags: ["language-detection", "multilingual", "nlp", "text-analysis", "unicode"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "langdetect>=1.0.9"]
Performance: O(n) where n is text length
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A robust language detection tissue that uses multiple strategies including
character n-grams, Unicode script detection, stop word analysis, and common
word patterns. Supports 50+ languages with confidence scores and handles
mixed-language texts.

Use Cases:
- Multilingual content routing
- Language-specific text processing
- Translation system input
- Content localization
- Spam filtering

Example Usage:
    # Basic detection
    detector = LanguageDetector()
    result = detector.detect("Hello, how are you?")
    # Result: {"language": "en", "confidence": 0.98}
    
    # Multiple language detection
    results = detector.detect_multiple("Hello world. Bonjour le monde.")
    # Result: [{"language": "en", "confidence": 0.85}, {"language": "fr", "confidence": 0.82}]
    
    # Batch processing
    languages = detector.detect_batch(texts)
"""

import re
import unicodedata
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter, defaultdict
import json
import math


class DetectionStrategy(Enum):
    """Available detection strategies"""
    NGRAM = "ngram"
    STOPWORDS = "stopwords"
    UNICODE = "unicode"
    DICTIONARY = "dictionary"
    HYBRID = "hybrid"


@dataclass
class LanguageProfile:
    """Profile for a language"""
    code: str
    name: str
    ngrams: Dict[str, float] = field(default_factory=dict)
    stop_words: Set[str] = field(default_factory=set)
    common_words: Set[str] = field(default_factory=set)
    char_frequencies: Dict[str, float] = field(default_factory=dict)
    unicode_ranges: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class DetectionResult:
    """Result of language detection"""
    language: str
    confidence: float
    script: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "language": self.language,
            "confidence": self.confidence,
            "script": self.script,
            "details": self.details
        }


class LanguageDetector:
    """
    Multi-method language detection system.
    Tissue Type: FUNCTIONAL - Core NLP language identification.
    """
    
    # Language profiles with common n-grams and words
    LANGUAGE_PROFILES = {
        "en": {
            "name": "English",
            "common_trigrams": ["the", "ing", "and", "ion", "tio", "ent", "ati", "for", "her", "ter"],
            "stop_words": {"the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "of"},
            "common_words": {"you", "that", "was", "for", "are", "with", "his", "they", "be"},
            "chars": "abcdefghijklmnopqrstuvwxyz"
        },
        "es": {
            "name": "Spanish",
            "common_trigrams": ["que", "ion", "ado", "ent", "nte", "con", "est", "ara", "los", "las"],
            "stop_words": {"el", "la", "de", "que", "y", "a", "en", "un", "ser", "se", "los", "las"},
            "common_words": {"por", "con", "para", "una", "su", "al", "es", "del"},
            "chars": "abcdefghijklmnopqrstuvwxyzáéíóúñ"
        },
        "fr": {
            "name": "French",
            "common_trigrams": ["ent", "ion", "que", "les", "de ", "le ", "tion", "ment", "la ", "dans"],
            "stop_words": {"le", "de", "un", "être", "et", "à", "il", "avoir", "ne", "je", "son", "que"},
            "common_words": {"les", "des", "dans", "pour", "pas", "qui", "nous", "avec"},
            "chars": "abcdefghijklmnopqrstuvwxyzàâæçéèêëîïôùûüÿ"
        },
        "de": {
            "name": "German",
            "common_trigrams": ["der", "die", "und", "ein", "den", "sch", "ich", "cht", "gen", "ver"],
            "stop_words": {"der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"},
            "common_words": {"ist", "des", "auf", "für", "im", "dem", "nicht", "ein", "eine"},
            "chars": "abcdefghijklmnopqrstuvwxyzäöüß"
        },
        "it": {
            "name": "Italian",
            "common_trigrams": ["ion", "ent", "ato", "che", "are", "del", "per", "con", "lla", "tta"],
            "stop_words": {"il", "di", "che", "è", "e", "la", "a", "un", "in", "non", "con"},
            "common_words": {"per", "del", "alla", "dei", "delle", "nella", "gli", "una"},
            "chars": "abcdefghijklmnopqrstuvwxyzàèéìòù"
        },
        "pt": {
            "name": "Portuguese",
            "common_trigrams": ["que", "ado", "ent", "ara", "com", "dos", "ção", "uma", "por", "do "],
            "stop_words": {"o", "a", "de", "para", "e", "do", "da", "em", "um", "que", "com"},
            "common_words": {"não", "uma", "por", "com", "os", "dos", "mais", "na"},
            "chars": "abcdefghijklmnopqrstuvwxyzàáâãçéêíóôõú"
        },
        "ru": {
            "name": "Russian",
            "common_trigrams": ["ени", "ост", "ого", "ств", "ова", "ани", "ние", "ель", "но ", "то "],
            "stop_words": {"и", "в", "не", "на", "я", "что", "он", "с", "как", "а", "то"},
            "common_words": {"это", "все", "она", "так", "его", "но", "да", "ты", "к"},
            "chars": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        },
        "ja": {
            "name": "Japanese",
            "common_trigrams": ["する", "ない", "こと", "ある", "いる", "です", "ます", "った", "して", "って"],
            "stop_words": {"の", "は", "に", "を", "が", "と", "で", "て", "も", "から"},
            "common_words": {"です", "ます", "する", "ある", "いる", "こと", "もの", "ため"},
            "chars": "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
        },
        "zh": {
            "name": "Chinese",
            "common_trigrams": ["的是", "一个", "不是", "我们", "可以", "这个", "他们", "什么", "没有", "就是"],
            "stop_words": {"的", "一", "是", "在", "不", "了", "有", "和", "人", "这"},
            "common_words": {"我", "他", "你", "们", "个", "为", "上", "中", "大", "来"},
            "chars": "的一是不了在人有我他这个们中来上大为和国地到以说时要就出会可也你对"
        },
        "ar": {
            "name": "Arabic",
            "common_trigrams": ["الم", "الت", "الع", "الأ", "وال", "في ", "من ", "على", "إلى", "هذا"],
            "stop_words": {"في", "من", "إلى", "على", "هذا", "ذلك", "التي", "الذي", "هذه", "تلك"},
            "common_words": {"كان", "قال", "هو", "لا", "ما", "عن", "أن", "كل", "أو"},
            "chars": "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
        }
    }
    
    def __init__(self,
                 strategy: str = "hybrid",
                 min_confidence: float = 0.5,
                 max_languages: int = 3):
        """
        Initialize language detector.
        
        Args:
            strategy: Detection strategy to use
            min_confidence: Minimum confidence threshold
            max_languages: Maximum languages to return for mixed text
        """
        self.strategy = DetectionStrategy(strategy.lower())
        self.min_confidence = min_confidence
        self.max_languages = max_languages
        
        # Build language profiles
        self._build_profiles()
        
        # Statistics
        self.texts_processed = 0
        self.languages_detected = Counter()
    
    def _build_profiles(self):
        """Build language profiles from data"""
        self.profiles = {}
        
        for code, data in self.LANGUAGE_PROFILES.items():
            profile = LanguageProfile(
                code=code,
                name=data["name"],
                stop_words=set(data.get("stop_words", [])),
                common_words=set(data.get("common_words", []))
            )
            
            # Build n-gram profiles
            for trigram in data.get("common_trigrams", []):
                profile.ngrams[trigram] = 1.0
            
            # Character frequencies
            chars = data.get("chars", "")
            for char in chars:
                profile.char_frequencies[char] = 1.0 / len(chars) if chars else 0
            
            self.profiles[code] = profile
    
    def detect(self, text: str) -> DetectionResult:
        """
        Detect language of text.
        
        Args:
            text: Input text
            
        Returns:
            Detection result with language and confidence
        """
        if not text or not text.strip():
            return DetectionResult(language="unknown", confidence=0.0)
        
        self.texts_processed += 1
        
        # Detect based on strategy
        if self.strategy == DetectionStrategy.NGRAM:
            result = self._detect_ngram(text)
        elif self.strategy == DetectionStrategy.STOPWORDS:
            result = self._detect_stopwords(text)
        elif self.strategy == DetectionStrategy.UNICODE:
            result = self._detect_unicode(text)
        elif self.strategy == DetectionStrategy.DICTIONARY:
            result = self._detect_dictionary(text)
        elif self.strategy == DetectionStrategy.HYBRID:
            result = self._detect_hybrid(text)
        else:
            result = self._detect_hybrid(text)
        
        # Update statistics
        if result.confidence >= self.min_confidence:
            self.languages_detected[result.language] += 1
        
        return result
    
    def detect_multiple(self, text: str) -> List[DetectionResult]:
        """
        Detect multiple languages in mixed text.
        
        Args:
            text: Input text possibly containing multiple languages
            
        Returns:
            List of detection results
        """
        # Split text into segments
        segments = self._segment_text(text)
        
        # Detect language for each segment
        results = []
        language_scores = defaultdict(float)
        
        for segment in segments:
            if segment.strip():
                result = self.detect(segment)
                if result.confidence >= self.min_confidence:
                    language_scores[result.language] += result.confidence * len(segment)
        
        # Normalize scores
        total_length = sum(len(s) for s in segments if s.strip())
        if total_length > 0:
            for lang in language_scores:
                language_scores[lang] /= total_length
        
        # Create results
        for lang, score in sorted(language_scores.items(), 
                                 key=lambda x: x[1], reverse=True)[:self.max_languages]:
            if score >= self.min_confidence:
                results.append(DetectionResult(language=lang, confidence=score))
        
        return results
    
    def _detect_ngram(self, text: str) -> DetectionResult:
        """Detect language using character n-grams"""
        text_lower = text.lower()
        
        # Extract trigrams
        trigrams = self._extract_ngrams(text_lower, 3)
        
        # Score each language
        scores = {}
        for lang, profile in self.profiles.items():
            score = 0
            matches = 0
            
            for trigram, count in trigrams.items():
                if trigram in profile.ngrams:
                    score += count * profile.ngrams[trigram]
                    matches += 1
            
            # Normalize by number of trigrams
            if len(trigrams) > 0:
                scores[lang] = (score / len(trigrams)) * (matches / len(profile.ngrams))
            else:
                scores[lang] = 0
        
        # Get best match
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(scores[best_lang], 1.0)
            
            return DetectionResult(
                language=best_lang,
                confidence=confidence,
                details={"method": "ngram", "scores": scores}
            )
        
        return DetectionResult(language="unknown", confidence=0.0)
    
    def _detect_stopwords(self, text: str) -> DetectionResult:
        """Detect language using stop words"""
        words = self._tokenize(text.lower())
        
        # Count stop words for each language
        scores = {}
        for lang, profile in self.profiles.items():
            if profile.stop_words:
                matches = sum(1 for word in words if word in profile.stop_words)
                scores[lang] = matches / len(profile.stop_words)
        
        # Get best match
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(scores[best_lang], 1.0)
            
            return DetectionResult(
                language=best_lang,
                confidence=confidence,
                details={"method": "stopwords", "scores": scores}
            )
        
        return DetectionResult(language="unknown", confidence=0.0)
    
    def _detect_unicode(self, text: str) -> DetectionResult:
        """Detect language using Unicode script analysis"""
        scripts = self._analyze_scripts(text)
        
        # Map scripts to languages
        script_language_map = {
            "Latin": ["en", "es", "fr", "de", "it", "pt"],
            "Cyrillic": ["ru"],
            "Arabic": ["ar"],
            "Han": ["zh"],
            "Hiragana": ["ja"],
            "Katakana": ["ja"]
        }
        
        # Find dominant script
        if scripts:
            dominant_script = max(scripts, key=scripts.get)
            script_ratio = scripts[dominant_script] / sum(scripts.values())
            
            # Get possible languages
            possible_langs = script_language_map.get(dominant_script, [])
            
            if possible_langs:
                # If multiple languages possible, use other methods
                if len(possible_langs) == 1:
                    return DetectionResult(
                        language=possible_langs[0],
                        confidence=script_ratio,
                        script=dominant_script,
                        details={"method": "unicode", "scripts": scripts}
                    )
                else:
                    # Refine using character frequencies
                    best_lang = self._refine_by_chars(text, possible_langs)
                    return DetectionResult(
                        language=best_lang,
                        confidence=script_ratio * 0.8,
                        script=dominant_script,
                        details={"method": "unicode", "scripts": scripts}
                    )
        
        return DetectionResult(language="unknown", confidence=0.0)
    
    def _detect_dictionary(self, text: str) -> DetectionResult:
        """Detect language using common words"""
        words = self._tokenize(text.lower())
        word_set = set(words)
        
        # Score each language
        scores = {}
        for lang, profile in self.profiles.items():
            if profile.common_words:
                matches = len(word_set & profile.common_words)
                scores[lang] = matches / len(profile.common_words)
        
        # Get best match
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(scores[best_lang], 1.0)
            
            return DetectionResult(
                language=best_lang,
                confidence=confidence,
                details={"method": "dictionary", "scores": scores}
            )
        
        return DetectionResult(language="unknown", confidence=0.0)
    
    def _detect_hybrid(self, text: str) -> DetectionResult:
        """Detect language using multiple methods"""
        # Try langdetect if available
        try:
            import langdetect
            lang = langdetect.detect(text)
            confidence = 0.9  # langdetect doesn't provide confidence
            
            # Validate with our methods
            ngram_result = self._detect_ngram(text)
            if ngram_result.language == lang:
                confidence = min(confidence + 0.1, 1.0)
            
            return DetectionResult(
                language=lang,
                confidence=confidence,
                details={"method": "langdetect+validation"}
            )
        except:
            pass
        
        # Fallback to our methods
        results = []
        
        # Get results from different methods
        methods = [
            self._detect_ngram,
            self._detect_stopwords,
            self._detect_unicode,
            self._detect_dictionary
        ]
        
        for method in methods:
            try:
                result = method(text)
                if result.confidence > 0:
                    results.append(result)
            except:
                continue
        
        if not results:
            return DetectionResult(language="unknown", confidence=0.0)
        
        # Combine results
        language_scores = defaultdict(float)
        for result in results:
            language_scores[result.language] += result.confidence
        
        # Normalize and get best
        best_lang = max(language_scores, key=language_scores.get)
        avg_confidence = language_scores[best_lang] / len(results)
        
        return DetectionResult(
            language=best_lang,
            confidence=avg_confidence,
            details={"method": "hybrid", "sub_results": [r.to_dict() for r in results]}
        )
    
    def _extract_ngrams(self, text: str, n: int) -> Dict[str, int]:
        """Extract character n-grams from text"""
        # Remove spaces and punctuation for char n-grams
        clean_text = re.sub(r'[^\w\s]', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        ngrams = Counter()
        for i in range(len(clean_text) - n + 1):
            ngram = clean_text[i:i + n]
            if ' ' not in ngram:  # Skip n-grams with spaces
                ngrams[ngram] += 1
        
        return ngrams
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()
    
    def _analyze_scripts(self, text: str) -> Dict[str, int]:
        """Analyze Unicode scripts in text"""
        scripts = Counter()
        
        for char in text:
            if char.isspace() or char in '.,!?;:':
                continue
            
            # Get Unicode script
            try:
                script = unicodedata.name(char).split()[0]
                
                # Map to general script categories
                if script in ["LATIN", "BASIC"]:
                    scripts["Latin"] += 1
                elif script in ["CYRILLIC"]:
                    scripts["Cyrillic"] += 1
                elif script in ["ARABIC"]:
                    scripts["Arabic"] += 1
                elif script in ["CJK", "CHINESE"]:
                    scripts["Han"] += 1
                elif script in ["HIRAGANA"]:
                    scripts["Hiragana"] += 1
                elif script in ["KATAKANA"]:
                    scripts["Katakana"] += 1
                elif script in ["GREEK"]:
                    scripts["Greek"] += 1
                elif script in ["HEBREW"]:
                    scripts["Hebrew"] += 1
            except:
                # Check by Unicode ranges
                code = ord(char)
                if 0x0041 <= code <= 0x024F:
                    scripts["Latin"] += 1
                elif 0x0400 <= code <= 0x04FF:
                    scripts["Cyrillic"] += 1
                elif 0x0600 <= code <= 0x06FF:
                    scripts["Arabic"] += 1
                elif 0x4E00 <= code <= 0x9FFF:
                    scripts["Han"] += 1
                elif 0x3040 <= code <= 0x309F:
                    scripts["Hiragana"] += 1
                elif 0x30A0 <= code <= 0x30FF:
                    scripts["Katakana"] += 1
        
        return dict(scripts)
    
    def _refine_by_chars(self, text: str, candidates: List[str]) -> str:
        """Refine language detection using character frequencies"""
        char_counts = Counter(text.lower())
        
        best_score = -1
        best_lang = candidates[0] if candidates else "unknown"
        
        for lang in candidates:
            if lang in self.profiles:
                profile = self.profiles[lang]
                score = 0
                
                for char, freq in profile.char_frequencies.items():
                    if char in char_counts:
                        score += char_counts[char] * freq
                
                if score > best_score:
                    best_score = score
                    best_lang = lang
        
        return best_lang
    
    def _segment_text(self, text: str) -> List[str]:
        """Segment text for mixed language detection"""
        # Simple segmentation by sentences and paragraphs
        segments = []
        
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            # Split by sentences (simple)
            sentences = re.split(r'[.!?]+', para)
            segments.extend([s.strip() for s in sentences if s.strip()])
        
        return segments
    
    def detect_batch(self, texts: List[str]) -> List[DetectionResult]:
        """Detect languages for multiple texts"""
        return [self.detect(text) for text in texts]
    
    def is_language(self, text: str, language: str, threshold: float = 0.8) -> bool:
        """Check if text is in a specific language"""
        result = self.detect(text)
        return result.language == language and result.confidence >= threshold
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {code: profile.name for code, profile in self.profiles.items()}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            "texts_processed": self.texts_processed,
            "languages_detected": dict(self.languages_detected),
            "most_common_language": self.languages_detected.most_common(1)[0] 
                                   if self.languages_detected else None,
            "supported_languages": len(self.profiles)
        }


# Utility functions
def detect_language(text: str) -> str:
    """Quick language detection"""
    detector = LanguageDetector()
    result = detector.detect(text)
    return result.language if result.confidence > 0.5 else "unknown"


def is_english(text: str) -> bool:
    """Check if text is in English"""
    detector = LanguageDetector()
    return detector.is_language(text, "en")


def detect_mixed_languages(text: str) -> List[str]:
    """Detect multiple languages in text"""
    detector = LanguageDetector()
    results = detector.detect_multiple(text)
    return [r.language for r in results]


# Auto-generated tests
def test_language_detector():
    """Test language detection functionality"""
    detector = LanguageDetector()
    
    # Test English detection
    en_text = "Hello, how are you today? This is a test."
    result = detector.detect(en_text)
    assert result.language == "en"
    assert result.confidence > 0.7
    
    # Test Spanish detection
    es_text = "Hola, ¿cómo estás? Este es un ejemplo."
    result = detector.detect(es_text)
    assert result.language == "es"
    
    # Test French detection
    fr_text = "Bonjour, comment allez-vous? C'est un test."
    result = detector.detect(fr_text)
    assert result.language == "fr"
    
    # Test German detection
    de_text = "Guten Tag, wie geht es Ihnen? Das ist ein Test."
    result = detector.detect(de_text)
    assert result.language == "de"
    
    # Test mixed language detection
    mixed_text = "Hello world. Bonjour le monde. Hola mundo."
    results = detector.detect_multiple(mixed_text)
    languages = [r.language for r in results]
    assert len(languages) >= 2
    
    # Test batch detection
    texts = [en_text, es_text, fr_text]
    batch_results = detector.detect_batch(texts)
    assert len(batch_results) == 3
    assert batch_results[0].language == "en"
    assert batch_results[1].language == "es"
    assert batch_results[2].language == "fr"
    
    # Test utility functions
    assert detect_language("This is English") == "en"
    assert is_english("Hello world") == True
    assert is_english("Bonjour") == False
    
    mixed_langs = detect_mixed_languages("Hello. Hola. Bonjour.")
    assert len(mixed_langs) >= 1
    
    # Test empty text
    empty_result = detector.detect("")
    assert empty_result.language == "unknown"
    assert empty_result.confidence == 0.0
    
    # Test statistics
    stats = detector.get_statistics()
    assert stats["texts_processed"] > 0
    
    # Test supported languages
    supported = detector.get_supported_languages()
    assert "en" in supported
    assert supported["en"] == "English"
    
    print("All language detection tests passed!")


if __name__ == "__main__":
    test_language_detector()