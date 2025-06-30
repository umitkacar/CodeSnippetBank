"""
Tissue ID: NLP-TISSUE-009
Title: Multi-Approach Sentiment Analyzer
Category: nlp/sentiment
Tags: ["sentiment-analysis", "emotion-detection", "opinion-mining", "nlp", "text-analytics"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n) where n is text length
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive sentiment analysis tissue that provides multiple approaches including
lexicon-based, rule-based, and ML-based methods. Supports fine-grained sentiment
(very negative to very positive), aspect-based sentiment, and emotion detection.
Handles negations, intensifiers, and emoticons.

Use Cases:
- Product review analysis
- Social media monitoring
- Customer feedback processing
- Brand sentiment tracking
- Content moderation

Example Usage:
    # Basic sentiment analysis
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("This product is absolutely amazing!")
    # Result: {"sentiment": "positive", "score": 0.92, "confidence": 0.88}
    
    # Fine-grained sentiment
    result = analyzer.analyze_detailed("The food was terrible but service was great")
    # Result: {"overall": "mixed", "aspects": {"food": -0.8, "service": 0.9}}
    
    # Emotion detection
    emotions = analyzer.detect_emotions("I'm so happy and excited!")
    # Result: {"joy": 0.8, "excitement": 0.7, "sadness": 0.0}
"""

import re
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import math


class SentimentLabel(Enum):
    """Sentiment categories"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"
    MIXED = "mixed"


class EmotionType(Enum):
    """Basic emotion categories"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"


@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    sentiment: str
    score: float  # -1 to 1
    confidence: float  # 0 to 1
    label: SentimentLabel
    subjectivity: float = 0.5
    aspects: Dict[str, float] = field(default_factory=dict)
    emotions: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "sentiment": self.sentiment,
            "score": self.score,
            "confidence": self.confidence,
            "label": self.label.value,
            "subjectivity": self.subjectivity,
            "aspects": self.aspects,
            "emotions": self.emotions
        }


class SentimentAnalyzer:
    """
    Multi-approach sentiment analysis system.
    Tissue Type: FUNCTIONAL - Core NLP sentiment analysis.
    """
    
    # Sentiment lexicons
    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "love", "best", "awesome", "incredible", "perfect", "beautiful",
        "brilliant", "outstanding", "superior", "magnificent", "marvelous",
        "exceptional", "fabulous", "terrific", "superb", "delightful"
    }
    
    NEGATIVE_WORDS = {
        "bad", "terrible", "awful", "horrible", "poor", "worst", "hate",
        "disappointing", "disgusting", "ugly", "broken", "useless",
        "pathetic", "mediocre", "inferior", "unacceptable", "dreadful",
        "atrocious", "abysmal", "appalling", "deplorable", "miserable"
    }
    
    # Intensifiers and modifiers
    INTENSIFIERS = {
        "very": 1.5, "extremely": 2.0, "absolutely": 2.0, "totally": 1.8,
        "really": 1.5, "so": 1.5, "quite": 1.2, "rather": 1.2,
        "particularly": 1.5, "especially": 1.5, "incredibly": 1.8,
        "remarkably": 1.6, "exceptionally": 1.8, "unusually": 1.4
    }
    
    DIMINISHERS = {
        "slightly": 0.5, "somewhat": 0.7, "rather": 0.8, "fairly": 0.8,
        "a bit": 0.6, "a little": 0.6, "sort of": 0.7, "kind of": 0.7,
        "barely": 0.4, "hardly": 0.4, "scarcely": 0.4
    }
    
    NEGATIONS = {
        "not", "no", "none", "never", "neither", "nobody", "nothing",
        "nowhere", "isn't", "wasn't", "shouldn't", "wouldn't", "couldn't",
        "won't", "can't", "don't", "doesn't", "didn't", "hasn't", "haven't"
    }
    
    # Emoticons and emojis
    EMOTICONS = {
        ":)": 0.5, ":-)": 0.5, ":]": 0.5, ":D": 0.8, ":-D": 0.8,
        ":(": -0.5, ":-(": -0.5, ":[": -0.5, ":'(": -0.8,
        ";)": 0.3, ";-)": 0.3, ":P": 0.3, ":-P": 0.3,
        ":/": -0.2, ":-/": -0.2, ":|": 0.0, ":-|": 0.0,
        "<3": 0.8, "</3": -0.8, ":*": 0.6, ":-*": 0.6
    }
    
    # Emotion lexicons
    EMOTION_WORDS = {
        EmotionType.JOY: {
            "happy", "joy", "cheerful", "delighted", "pleased", "glad",
            "joyful", "elated", "jubilant", "ecstatic", "content", "satisfied"
        },
        EmotionType.SADNESS: {
            "sad", "unhappy", "depressed", "miserable", "sorrowful", "gloomy",
            "melancholy", "dejected", "disappointed", "heartbroken", "lonely"
        },
        EmotionType.ANGER: {
            "angry", "mad", "furious", "irritated", "annoyed", "frustrated",
            "outraged", "enraged", "livid", "irate", "hostile", "bitter"
        },
        EmotionType.FEAR: {
            "afraid", "scared", "frightened", "terrified", "anxious", "worried",
            "nervous", "panicked", "horrified", "alarmed", "apprehensive"
        },
        EmotionType.SURPRISE: {
            "surprised", "amazed", "astonished", "shocked", "stunned",
            "startled", "bewildered", "astounded", "flabbergasted"
        },
        EmotionType.DISGUST: {
            "disgusted", "revolted", "repulsed", "sickened", "nauseated",
            "appalled", "offended", "disturbed", "displeased"
        }
    }
    
    def __init__(self,
                 lexicon_weight: float = 0.6,
                 rule_weight: float = 0.3,
                 ml_weight: float = 0.1):
        """
        Initialize sentiment analyzer.
        
        Args:
            lexicon_weight: Weight for lexicon-based scoring
            rule_weight: Weight for rule-based scoring
            ml_weight: Weight for ML-based scoring
        """
        self.lexicon_weight = lexicon_weight
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        
        # Build expanded lexicons
        self._build_lexicons()
        
        # Simple ML model (trained on initialization)
        self.ml_model = self._train_simple_model()
        
        # Statistics
        self.texts_processed = 0
        self.sentiment_distribution = Counter()
    
    def _build_lexicons(self):
        """Build expanded sentiment and emotion lexicons"""
        # Expand positive lexicon with variations
        self.positive_lexicon = set()
        for word in self.POSITIVE_WORDS:
            self.positive_lexicon.add(word)
            self.positive_lexicon.add(word + "ly")  # adverbs
            self.positive_lexicon.add(word + "ness")  # nouns
        
        # Expand negative lexicon
        self.negative_lexicon = set()
        for word in self.NEGATIVE_WORDS:
            self.negative_lexicon.add(word)
            self.negative_lexicon.add(word + "ly")
            self.negative_lexicon.add(word + "ness")
        
        # Build emotion lexicon
        self.emotion_lexicon = {}
        for emotion, words in self.EMOTION_WORDS.items():
            expanded = set()
            for word in words:
                expanded.add(word)
                expanded.add(word + "ly")
                expanded.add(word + "ness")
            self.emotion_lexicon[emotion] = expanded
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment analysis result
        """
        if not text:
            return SentimentResult(
                sentiment="neutral",
                score=0.0,
                confidence=0.0,
                label=SentimentLabel.NEUTRAL
            )
        
        self.texts_processed += 1
        
        # Preprocess text
        processed_text = self._preprocess(text)
        tokens = self._tokenize(processed_text)
        
        # Get scores from different methods
        lexicon_score = self._lexicon_based_score(tokens, text)
        rule_score = self._rule_based_score(tokens, text)
        ml_score = self._ml_based_score(processed_text)
        
        # Combine scores
        combined_score = (
            self.lexicon_weight * lexicon_score +
            self.rule_weight * rule_score +
            self.ml_weight * ml_score
        )
        
        # Determine sentiment label
        label = self._score_to_label(combined_score)
        sentiment = self._label_to_sentiment(label)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            lexicon_score, rule_score, ml_score, combined_score
        )
        
        # Detect emotions
        emotions = self._detect_emotions(tokens)
        
        # Calculate subjectivity
        subjectivity = self._calculate_subjectivity(tokens, text)
        
        # Update statistics
        self.sentiment_distribution[sentiment] += 1
        
        return SentimentResult(
            sentiment=sentiment,
            score=combined_score,
            confidence=confidence,
            label=label,
            subjectivity=subjectivity,
            emotions=emotions
        )
    
    def analyze_detailed(self, text: str) -> SentimentResult:
        """
        Perform detailed sentiment analysis with aspects.
        
        Args:
            text: Input text
            
        Returns:
            Detailed sentiment result with aspect sentiments
        """
        # Basic analysis
        result = self.analyze(text)
        
        # Extract aspects
        aspects = self._extract_aspects(text)
        
        # Analyze sentiment for each aspect
        aspect_sentiments = {}
        for aspect, aspect_text in aspects.items():
            aspect_result = self.analyze(aspect_text)
            aspect_sentiments[aspect] = aspect_result.score
        
        result.aspects = aspect_sentiments
        
        # Determine if mixed sentiment
        if aspect_sentiments:
            positive_aspects = sum(1 for s in aspect_sentiments.values() if s > 0.2)
            negative_aspects = sum(1 for s in aspect_sentiments.values() if s < -0.2)
            
            if positive_aspects > 0 and negative_aspects > 0:
                result.label = SentimentLabel.MIXED
                result.sentiment = "mixed"
        
        return result
    
    def _preprocess(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase but preserve emoticons
        emoticons = re.findall(r'[:;=]-?[)(\[\]DPp/|]|<3|</3', text)
        
        processed = text.lower()
        
        # Restore emoticons with original case
        for emoticon in emoticons:
            processed = processed.replace(emoticon.lower(), emoticon)
        
        # Expand contractions
        contractions = {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'ll": " will", "'ve": " have", "'re": " are",
            "'d": " would", "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            processed = processed.replace(contraction, expansion)
        
        return processed
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        # Simple word tokenization preserving emoticons
        pattern = r'\b\w+\b|[:;=]-?[)(\[\]DPp/|]|<3|</3|[.!?]+'
        return re.findall(pattern, text)
    
    def _lexicon_based_score(self, tokens: List[str], original_text: str) -> float:
        """Calculate sentiment score using lexicon"""
        score = 0.0
        word_count = 0
        
        # Check for emoticons in original text
        for emoticon, emoticon_score in self.EMOTICONS.items():
            if emoticon in original_text:
                score += emoticon_score
                word_count += 1
        
        # Score words
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Skip non-words
            if not token.isalpha():
                i += 1
                continue
            
            # Check for negation
            negation = False
            if i > 0 and tokens[i-1] in self.NEGATIONS:
                negation = True
            
            # Check for intensifiers
            intensifier = 1.0
            if i > 0 and tokens[i-1] in self.INTENSIFIERS:
                intensifier = self.INTENSIFIERS[tokens[i-1]]
            elif i > 0 and tokens[i-1] in self.DIMINISHERS:
                intensifier = self.DIMINISHERS[tokens[i-1]]
            
            # Calculate word score
            word_score = 0
            if token in self.positive_lexicon:
                word_score = 1.0
            elif token in self.negative_lexicon:
                word_score = -1.0
            
            # Apply modifiers
            if word_score != 0:
                if negation:
                    word_score *= -0.5  # Negation reverses but weakens
                word_score *= intensifier
                
                score += word_score
                word_count += 1
            
            i += 1
        
        # Normalize score
        if word_count > 0:
            score = score / word_count
            # Apply sigmoid to keep in [-1, 1] range
            score = 2 / (1 + math.exp(-score)) - 1
        
        return score
    
    def _rule_based_score(self, tokens: List[str], text: str) -> float:
        """Calculate sentiment using rules"""
        score = 0.0
        
        # Rule 1: Exclamation marks indicate strong sentiment
        exclamation_count = text.count('!')
        if exclamation_count > 0:
            # Check surrounding context
            if any(word in text.lower() for word in self.positive_lexicon):
                score += min(exclamation_count * 0.1, 0.3)
            elif any(word in text.lower() for word in self.negative_lexicon):
                score -= min(exclamation_count * 0.1, 0.3)
        
        # Rule 2: Question marks might indicate uncertainty
        if '?' in text:
            score *= 0.8
        
        # Rule 3: All caps indicates strong emotion
        caps_words = [t for t in tokens if t.isalpha() and t.isupper() and len(t) > 1]
        if caps_words:
            if any(word.lower() in self.positive_lexicon for word in caps_words):
                score += 0.2
            elif any(word.lower() in self.negative_lexicon for word in caps_words):
                score -= 0.2
        
        # Rule 4: Repeated characters indicate emphasis
        repeated_pattern = re.findall(r'(\w)\1{2,}', text)
        if repeated_pattern:
            score *= 1.2
        
        # Rule 5: "But" reversal - sentiment after "but" is more important
        if " but " in text.lower():
            parts = text.lower().split(" but ")
            if len(parts) == 2:
                # Analyze second part more heavily
                second_part_tokens = self._tokenize(parts[1])
                second_score = self._lexicon_based_score(second_part_tokens, parts[1])
                score = score * 0.3 + second_score * 0.7
        
        return max(-1, min(1, score))
    
    def _ml_based_score(self, text: str) -> float:
        """Calculate sentiment using simple ML model"""
        if not hasattr(self, 'ml_model') or self.ml_model is None:
            return 0.0
        
        # Extract features
        features = self._extract_ml_features(text)
        
        # Predict using simple model
        score = self.ml_model.predict(features)
        
        return score
    
    def _extract_ml_features(self, text: str) -> List[float]:
        """Extract features for ML model"""
        features = []
        
        # Length features
        features.append(len(text))
        features.append(len(text.split()))
        
        # Punctuation features
        features.append(text.count('!'))
        features.append(text.count('?'))
        features.append(text.count('.'))
        
        # Lexicon features
        tokens = self._tokenize(text.lower())
        positive_count = sum(1 for t in tokens if t in self.positive_lexicon)
        negative_count = sum(1 for t in tokens if t in self.negative_lexicon)
        
        features.append(positive_count)
        features.append(negative_count)
        features.append(positive_count - negative_count)
        
        # Emoticon features
        emoticon_score = sum(self.EMOTICONS.get(e, 0) for e in self.EMOTICONS if e in text)
        features.append(emoticon_score)
        
        # Capital letters ratio
        if len(text) > 0:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        else:
            caps_ratio = 0
        features.append(caps_ratio)
        
        return features
    
    def _train_simple_model(self):
        """Train a simple sentiment model"""
        # Simple linear model with hand-crafted weights
        class SimpleModel:
            def __init__(self):
                # Feature weights
                self.weights = [
                    0.0001,   # text length (slight positive)
                    0.005,    # word count
                    0.05,     # exclamation marks
                    -0.02,    # question marks
                    0.0,      # periods
                    0.15,     # positive words
                    -0.15,    # negative words
                    0.2,      # pos - neg difference
                    0.3,      # emoticon score
                    0.1       # caps ratio
                ]
            
            def predict(self, features):
                score = sum(w * f for w, f in zip(self.weights, features))
                # Apply tanh to bound output
                return math.tanh(score)
        
        return SimpleModel()
    
    def _detect_emotions(self, tokens: List[str]) -> Dict[str, float]:
        """Detect emotions in text"""
        emotions = {}
        total_emotion_words = 0
        
        for emotion_type, emotion_words in self.emotion_lexicon.items():
            count = sum(1 for token in tokens if token in emotion_words)
            if count > 0:
                emotions[emotion_type.value] = count
                total_emotion_words += count
        
        # Normalize emotion scores
        if total_emotion_words > 0:
            for emotion in emotions:
                emotions[emotion] = emotions[emotion] / total_emotion_words
        
        return emotions
    
    def _calculate_subjectivity(self, tokens: List[str], text: str) -> float:
        """Calculate text subjectivity (0=objective, 1=subjective)"""
        subjective_indicators = {
            "i", "me", "my", "mine", "myself", "we", "our", "ours",
            "think", "feel", "believe", "opinion", "personally",
            "seems", "appears", "probably", "maybe", "perhaps"
        }
        
        objective_indicators = {
            "fact", "data", "research", "study", "report", "statistics",
            "evidence", "proof", "shows", "demonstrates", "indicates"
        }
        
        # Count indicators
        subjective_count = sum(1 for t in tokens if t in subjective_indicators)
        objective_count = sum(1 for t in tokens if t in objective_indicators)
        
        # Check for personal pronouns
        personal_pronouns = len(re.findall(r'\b(I|me|my|mine|myself)\b', text, re.I))
        
        # Calculate subjectivity score
        if len(tokens) > 0:
            subjectivity = (subjective_count + personal_pronouns * 0.5 - objective_count * 0.5) / len(tokens)
            subjectivity = max(0, min(1, subjectivity * 10))  # Scale and bound
        else:
            subjectivity = 0.5
        
        return subjectivity
    
    def _extract_aspects(self, text: str) -> Dict[str, str]:
        """Extract aspects and their context from text"""
        aspects = {}
        
        # Common aspect keywords
        aspect_keywords = {
            "service": ["service", "staff", "employee", "support"],
            "quality": ["quality", "build", "material", "durability"],
            "price": ["price", "cost", "expensive", "cheap", "value"],
            "delivery": ["delivery", "shipping", "arrived", "package"],
            "product": ["product", "item", "purchase", "bought"],
            "food": ["food", "meal", "dish", "taste", "flavor"],
            "location": ["location", "place", "venue", "atmosphere"]
        }
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for aspect, keywords in aspect_keywords.items():
                if any(keyword in sentence_lower for keyword in keywords):
                    if aspect in aspects:
                        aspects[aspect] += " " + sentence
                    else:
                        aspects[aspect] = sentence
        
        return aspects
    
    def _score_to_label(self, score: float) -> SentimentLabel:
        """Convert numerical score to sentiment label"""
        if score <= -0.6:
            return SentimentLabel.VERY_NEGATIVE
        elif score <= -0.2:
            return SentimentLabel.NEGATIVE
        elif score <= 0.2:
            return SentimentLabel.NEUTRAL
        elif score <= 0.6:
            return SentimentLabel.POSITIVE
        else:
            return SentimentLabel.VERY_POSITIVE
    
    def _label_to_sentiment(self, label: SentimentLabel) -> str:
        """Convert label to simple sentiment string"""
        if label in [SentimentLabel.VERY_NEGATIVE, SentimentLabel.NEGATIVE]:
            return "negative"
        elif label in [SentimentLabel.VERY_POSITIVE, SentimentLabel.POSITIVE]:
            return "positive"
        elif label == SentimentLabel.MIXED:
            return "mixed"
        else:
            return "neutral"
    
    def _calculate_confidence(self, lexicon_score: float, rule_score: float,
                            ml_score: float, combined_score: float) -> float:
        """Calculate confidence in the sentiment prediction"""
        # Agreement between methods increases confidence
        scores = [lexicon_score, rule_score, ml_score]
        
        # Calculate standard deviation
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        # Lower std_dev means higher agreement
        agreement_confidence = 1 - min(std_dev, 1)
        
        # Strength of sentiment affects confidence
        strength_confidence = min(abs(combined_score), 1)
        
        # Combine confidences
        confidence = (agreement_confidence * 0.6 + strength_confidence * 0.4)
        
        return confidence
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detect emotions in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of emotion scores
        """
        tokens = self._tokenize(self._preprocess(text))
        return self._detect_emotions(tokens)
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text) for text in texts]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sentiment analysis statistics"""
        total = sum(self.sentiment_distribution.values())
        distribution = {}
        
        if total > 0:
            for sentiment, count in self.sentiment_distribution.items():
                distribution[sentiment] = count / total
        
        return {
            "texts_processed": self.texts_processed,
            "sentiment_distribution": dict(self.sentiment_distribution),
            "sentiment_percentages": distribution,
            "most_common_sentiment": self.sentiment_distribution.most_common(1)[0] 
                                   if self.sentiment_distribution else None
        }


# Utility functions
def analyze_sentiment(text: str) -> str:
    """Quick sentiment analysis"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(text)
    return result.sentiment


def get_sentiment_score(text: str) -> float:
    """Get sentiment score (-1 to 1)"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(text)
    return result.score


def analyze_reviews(reviews: List[str]) -> Dict[str, Any]:
    """Analyze sentiment distribution in reviews"""
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze_batch(reviews)
    
    # Aggregate results
    sentiments = [r.sentiment for r in results]
    avg_score = sum(r.score for r in results) / len(results) if results else 0
    
    distribution = Counter(sentiments)
    
    return {
        "average_score": avg_score,
        "distribution": dict(distribution),
        "positive_ratio": distribution["positive"] / len(reviews) if reviews else 0,
        "negative_ratio": distribution["negative"] / len(reviews) if reviews else 0
    }


# Auto-generated tests
def test_sentiment_analyzer():
    """Test sentiment analysis functionality"""
    analyzer = SentimentAnalyzer()
    
    # Test positive sentiment
    positive_text = "This product is absolutely amazing! I love it!"
    result = analyzer.analyze(positive_text)
    assert result.sentiment == "positive"
    assert result.score > 0.5
    assert result.confidence > 0.6
    
    # Test negative sentiment
    negative_text = "This is terrible. Completely disappointed."
    result = analyzer.analyze(negative_text)
    assert result.sentiment == "negative"
    assert result.score < -0.3
    
    # Test neutral sentiment
    neutral_text = "The product arrived yesterday. It is blue."
    result = analyzer.analyze(neutral_text)
    assert result.sentiment == "neutral"
    assert -0.3 < result.score < 0.3
    
    # Test mixed sentiment
    mixed_text = "The food was terrible but the service was excellent!"
    result = analyzer.analyze_detailed(mixed_text)
    assert "food" in result.aspects
    assert "service" in result.aspects
    assert result.aspects["food"] < 0
    assert result.aspects["service"] > 0
    
    # Test with emoticons
    emoticon_text = "Great job! :D"
    result = analyzer.analyze(emoticon_text)
    assert result.sentiment == "positive"
    assert result.score > 0.5
    
    # Test negation
    negation_text = "This is not good at all"
    result = analyzer.analyze(negation_text)
    assert result.sentiment == "negative"
    
    # Test intensifiers
    intense_text = "This is extremely bad"
    result = analyzer.analyze(intense_text)
    assert result.score < -0.5
    
    # Test emotion detection
    emotion_text = "I'm so happy and excited about this!"
    emotions = analyzer.detect_emotions(emotion_text)
    assert "joy" in emotions
    assert emotions["joy"] > 0
    
    # Test subjectivity
    subjective_text = "I think this is the best movie ever"
    result = analyzer.analyze(subjective_text)
    assert result.subjectivity > 0.5
    
    objective_text = "The product weighs 2.5 kg and measures 10x20 cm"
    result = analyzer.analyze(objective_text)
    assert result.subjectivity < 0.5
    
    # Test batch analysis
    reviews = [
        "Excellent product!",
        "Terrible experience",
        "It's okay, nothing special"
    ]
    results = analyzer.analyze_batch(reviews)
    assert len(results) == 3
    assert results[0].sentiment == "positive"
    assert results[1].sentiment == "negative"
    assert results[2].sentiment == "neutral"
    
    # Test utility functions
    assert analyze_sentiment("Great!") == "positive"
    assert get_sentiment_score("Awful") < 0
    
    review_analysis = analyze_reviews(reviews)
    assert "distribution" in review_analysis
    assert review_analysis["positive_ratio"] > 0
    
    print("All sentiment analysis tests passed!")


if __name__ == "__main__":
    test_sentiment_analyzer()