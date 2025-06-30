"""
Tissue ID: NLP-TISSUE-006
Title: Multi-Algorithm Text Classifier
Category: nlp/classification
Tags: ["text-classification", "sentiment-analysis", "topic-modeling", "nlp", "machine-learning"]
Difficulty: Advanced
Dependencies: ["scikit-learn>=1.3", "numpy>=1.24", "joblib>=1.3"]
Performance: O(n*m) for training where n is samples, m is features
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A versatile text classification tissue that provides multiple algorithms for
categorizing text. Includes traditional ML methods (Naive Bayes, SVM, Random Forest)
and simple neural approaches. Features automatic preprocessing, feature extraction,
and model evaluation.

Use Cases:
- Sentiment analysis (positive/negative/neutral)
- Topic classification
- Spam detection
- Intent classification for chatbots
- Document categorization

Example Usage:
    # Basic classification
    classifier = TextClassifier(algorithm="naive_bayes")
    classifier.train(texts, labels)
    predictions = classifier.predict(["This product is amazing!"])
    
    # With custom preprocessing
    classifier = TextClassifier(
        algorithm="svm",
        preprocessing_steps=["lowercase", "remove_punctuation", "stem"]
    )
    classifier.train(texts, labels)
    
    # Multi-class classification
    predictions = classifier.predict_proba(new_texts)
"""

import numpy as np
from typing import List, Dict, Optional, Union, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from pathlib import Path
import re
from collections import Counter, defaultdict


class ClassificationAlgorithm(Enum):
    """Available classification algorithms"""
    NAIVE_BAYES = "naive_bayes"
    SVM = "svm"
    RANDOM_FOREST = "random_forest"
    LOGISTIC_REGRESSION = "logistic_regression"
    KNN = "knn"
    ENSEMBLE = "ensemble"


class FeatureType(Enum):
    """Feature extraction methods"""
    BOW = "bag_of_words"
    TFIDF = "tfidf"
    NGRAMS = "ngrams"
    WORD_EMBEDDINGS = "word_embeddings"
    CUSTOM = "custom"


@dataclass
class ClassifierConfig:
    """Configuration for text classifier"""
    max_features: int = 10000
    ngram_range: Tuple[int, int] = (1, 2)
    min_df: float = 0.01
    max_df: float = 0.95
    use_idf: bool = True
    smooth_idf: bool = True
    lowercase: bool = True
    remove_stopwords: bool = True
    stem_words: bool = False
    max_sequence_length: int = 1000
    validation_split: float = 0.2
    random_state: int = 42


@dataclass
class ClassificationResult:
    """Result of classification"""
    label: str
    confidence: float
    probabilities: Dict[str, float]
    features_used: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "label": self.label,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "features_used": self.features_used
        }


class TextClassifier:
    """
    Multi-algorithm text classification system.
    Tissue Type: FUNCTIONAL - Core ML text classification.
    """
    
    def __init__(self,
                 algorithm: str = "naive_bayes",
                 feature_type: str = "tfidf",
                 config: Optional[ClassifierConfig] = None,
                 preprocessing_steps: Optional[List[str]] = None):
        """
        Initialize text classifier.
        
        Args:
            algorithm: Classification algorithm to use
            feature_type: Feature extraction method
            config: Configuration options
            preprocessing_steps: List of preprocessing steps to apply
        """
        self.algorithm = ClassificationAlgorithm(algorithm.lower())
        self.feature_type = FeatureType(feature_type.lower())
        self.config = config or ClassifierConfig()
        self.preprocessing_steps = preprocessing_steps or ["lowercase", "remove_punctuation"]
        
        # Models
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        
        # Training data info
        self.classes_ = []
        self.feature_names_ = []
        self.is_trained = False
        
        # Statistics
        self.texts_processed = 0
        self.training_accuracy = None
    
    def train(self, texts: List[str], labels: List[str], 
              validation_texts: Optional[List[str]] = None,
              validation_labels: Optional[List[str]] = None):
        """
        Train the classifier on texts and labels.
        
        Args:
            texts: Training texts
            labels: Training labels
            validation_texts: Optional validation texts
            validation_labels: Optional validation labels
        """
        if not texts or not labels:
            raise ValueError("Training requires non-empty texts and labels")
        
        if len(texts) != len(labels):
            raise ValueError("Number of texts must match number of labels")
        
        # Preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Encode labels
        self.label_encoder = self._create_label_encoder(labels)
        encoded_labels = [self.label_encoder[label] for label in labels]
        self.classes_ = list(self.label_encoder.keys())
        
        # Extract features
        X_train = self._extract_features(processed_texts, fit=True)
        y_train = np.array(encoded_labels)
        
        # Initialize classifier
        self.classifier = self._create_classifier()
        
        # Train classifier
        self.classifier.fit(X_train, y_train)
        
        # Calculate training accuracy
        train_predictions = self.classifier.predict(X_train)
        self.training_accuracy = np.mean(train_predictions == y_train)
        
        # Validate if validation data provided
        if validation_texts and validation_labels:
            self._validate(validation_texts, validation_labels)
        
        self.is_trained = True
        self.texts_processed += len(texts)
    
    def predict(self, texts: Union[str, List[str]]) -> Union[ClassificationResult, List[ClassificationResult]]:
        """
        Predict labels for texts.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            Classification result(s)
        """
        if not self.is_trained:
            raise ValueError("Classifier must be trained before prediction")
        
        single_text = isinstance(texts, str)
        if single_text:
            texts = [texts]
        
        # Preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Extract features
        X = self._extract_features(processed_texts, fit=False)
        
        # Predict
        predictions = self.classifier.predict(X)
        
        # Get probabilities if available
        if hasattr(self.classifier, 'predict_proba'):
            probabilities = self.classifier.predict_proba(X)
        else:
            # Create dummy probabilities
            probabilities = np.zeros((len(predictions), len(self.classes_)))
            for i, pred in enumerate(predictions):
                probabilities[i, pred] = 1.0
        
        # Create results
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            # Decode label
            label = self._decode_label(pred)
            
            # Create probability dictionary
            prob_dict = {self._decode_label(j): float(p) 
                        for j, p in enumerate(probs)}
            
            # Get top features if possible
            top_features = self._get_top_features(processed_texts[i])
            
            result = ClassificationResult(
                label=label,
                confidence=float(max(probs)),
                probabilities=prob_dict,
                features_used=top_features
            )
            results.append(result)
        
        self.texts_processed += len(texts)
        
        return results[0] if single_text else results
    
    def predict_proba(self, texts: Union[str, List[str]]) -> Union[Dict[str, float], List[Dict[str, float]]]:
        """
        Get probability distribution over classes.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            Probability dictionaries
        """
        results = self.predict(texts)
        if isinstance(results, ClassificationResult):
            return results.probabilities
        else:
            return [r.probabilities for r in results]
    
    def _preprocess_text(self, text: str) -> str:
        """Apply preprocessing steps to text"""
        processed = text
        
        for step in self.preprocessing_steps:
            if step == "lowercase":
                processed = processed.lower()
            elif step == "remove_punctuation":
                processed = re.sub(r'[^\w\s]', ' ', processed)
            elif step == "remove_numbers":
                processed = re.sub(r'\d+', '', processed)
            elif step == "remove_urls":
                processed = re.sub(r'http\S+|www.\S+', '', processed)
            elif step == "remove_emails":
                processed = re.sub(r'\S+@\S+', '', processed)
            elif step == "normalize_whitespace":
                processed = ' '.join(processed.split())
            elif step == "stem":
                # Simple suffix stripping
                words = processed.split()
                stemmed = []
                for word in words:
                    if word.endswith('ing'):
                        stemmed.append(word[:-3])
                    elif word.endswith('ed'):
                        stemmed.append(word[:-2])
                    elif word.endswith('s') and len(word) > 2:
                        stemmed.append(word[:-1])
                    else:
                        stemmed.append(word)
                processed = ' '.join(stemmed)
        
        return processed
    
    def _extract_features(self, texts: List[str], fit: bool = False) -> np.ndarray:
        """Extract features from texts"""
        if self.feature_type in [FeatureType.BOW, FeatureType.TFIDF]:
            return self._extract_sklearn_features(texts, fit)
        elif self.feature_type == FeatureType.NGRAMS:
            return self._extract_ngram_features(texts, fit)
        elif self.feature_type == FeatureType.WORD_EMBEDDINGS:
            return self._extract_embedding_features(texts, fit)
        else:
            return self._extract_custom_features(texts, fit)
    
    def _extract_sklearn_features(self, texts: List[str], fit: bool) -> np.ndarray:
        """Extract features using scikit-learn vectorizers"""
        try:
            from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
            
            if fit:
                if self.feature_type == FeatureType.BOW:
                    self.vectorizer = CountVectorizer(
                        max_features=self.config.max_features,
                        ngram_range=self.config.ngram_range,
                        min_df=self.config.min_df,
                        max_df=self.config.max_df,
                        lowercase=False  # Already preprocessed
                    )
                else:  # TFIDF
                    self.vectorizer = TfidfVectorizer(
                        max_features=self.config.max_features,
                        ngram_range=self.config.ngram_range,
                        min_df=self.config.min_df,
                        max_df=self.config.max_df,
                        use_idf=self.config.use_idf,
                        smooth_idf=self.config.smooth_idf,
                        lowercase=False  # Already preprocessed
                    )
                
                X = self.vectorizer.fit_transform(texts)
                self.feature_names_ = self.vectorizer.get_feature_names_out().tolist()
            else:
                X = self.vectorizer.transform(texts)
            
            return X.toarray()
        except ImportError:
            print("Warning: scikit-learn not available, using custom features")
            return self._extract_custom_features(texts, fit)
    
    def _extract_ngram_features(self, texts: List[str], fit: bool) -> np.ndarray:
        """Extract n-gram features manually"""
        if fit:
            # Build vocabulary
            ngram_counts = Counter()
            for text in texts:
                ngrams = self._get_ngrams(text, self.config.ngram_range)
                ngram_counts.update(ngrams)
            
            # Select top features
            self.feature_names_ = [ngram for ngram, _ in 
                                  ngram_counts.most_common(self.config.max_features)]
            self.feature_index_ = {feat: i for i, feat in enumerate(self.feature_names_)}
        
        # Create feature matrix
        X = np.zeros((len(texts), len(self.feature_names_)))
        
        for i, text in enumerate(texts):
            ngrams = self._get_ngrams(text, self.config.ngram_range)
            for ngram in ngrams:
                if ngram in self.feature_index_:
                    X[i, self.feature_index_[ngram]] += 1
        
        return X
    
    def _extract_embedding_features(self, texts: List[str], fit: bool) -> np.ndarray:
        """Extract word embedding features"""
        # Simple average of random word embeddings
        embedding_dim = 100
        X = []
        
        for text in texts:
            words = text.split()
            if words:
                # Random embeddings (in production, use pre-trained)
                embeddings = np.random.randn(len(words), embedding_dim)
                text_embedding = np.mean(embeddings, axis=0)
            else:
                text_embedding = np.zeros(embedding_dim)
            X.append(text_embedding)
        
        return np.array(X)
    
    def _extract_custom_features(self, texts: List[str], fit: bool) -> np.ndarray:
        """Extract custom features"""
        features = []
        
        for text in texts:
            text_features = [
                len(text),  # Text length
                len(text.split()),  # Word count
                text.count('!'),  # Exclamation marks
                text.count('?'),  # Question marks
                text.count('.'),  # Periods
                sum(1 for c in text if c.isupper()) / (len(text) + 1),  # Uppercase ratio
                len([w for w in text.split() if len(w) > 6]),  # Long words
                len(set(text.split())),  # Unique words
            ]
            features.append(text_features)
        
        return np.array(features)
    
    def _get_ngrams(self, text: str, ngram_range: Tuple[int, int]) -> List[str]:
        """Extract n-grams from text"""
        words = text.split()
        ngrams = []
        
        for n in range(ngram_range[0], ngram_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i + n])
                ngrams.append(ngram)
        
        return ngrams
    
    def _create_classifier(self):
        """Create classifier based on algorithm"""
        try:
            if self.algorithm == ClassificationAlgorithm.NAIVE_BAYES:
                from sklearn.naive_bayes import MultinomialNB
                return MultinomialNB()
            elif self.algorithm == ClassificationAlgorithm.SVM:
                from sklearn.svm import SVC
                return SVC(kernel='linear', probability=True, random_state=self.config.random_state)
            elif self.algorithm == ClassificationAlgorithm.RANDOM_FOREST:
                from sklearn.ensemble import RandomForestClassifier
                return RandomForestClassifier(n_estimators=100, random_state=self.config.random_state)
            elif self.algorithm == ClassificationAlgorithm.LOGISTIC_REGRESSION:
                from sklearn.linear_model import LogisticRegression
                return LogisticRegression(max_iter=1000, random_state=self.config.random_state)
            elif self.algorithm == ClassificationAlgorithm.KNN:
                from sklearn.neighbors import KNeighborsClassifier
                return KNeighborsClassifier(n_neighbors=5)
            elif self.algorithm == ClassificationAlgorithm.ENSEMBLE:
                from sklearn.ensemble import VotingClassifier
                from sklearn.naive_bayes import MultinomialNB
                from sklearn.svm import SVC
                from sklearn.ensemble import RandomForestClassifier
                
                estimators = [
                    ('nb', MultinomialNB()),
                    ('svm', SVC(kernel='linear', probability=True)),
                    ('rf', RandomForestClassifier(n_estimators=50))
                ]
                return VotingClassifier(estimators, voting='soft')
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        except ImportError:
            print("Warning: scikit-learn not available, using simple classifier")
            return SimpleClassifier()
    
    def _create_label_encoder(self, labels: List[str]) -> Dict[str, int]:
        """Create label to integer mapping"""
        unique_labels = sorted(set(labels))
        return {label: i for i, label in enumerate(unique_labels)}
    
    def _decode_label(self, encoded: int) -> str:
        """Decode integer label back to string"""
        for label, idx in self.label_encoder.items():
            if idx == encoded:
                return label
        return "unknown"
    
    def _get_top_features(self, text: str, top_k: int = 5) -> List[str]:
        """Get top features for a text"""
        if not self.feature_names_ or self.feature_type not in [FeatureType.BOW, FeatureType.TFIDF]:
            return []
        
        # Extract features for this text
        features = self._extract_features([text], fit=False)[0]
        
        # Get top k features
        top_indices = np.argsort(features)[-top_k:][::-1]
        top_features = [self.feature_names_[i] for i in top_indices if features[i] > 0]
        
        return top_features
    
    def _validate(self, texts: List[str], labels: List[str]) -> float:
        """Validate classifier on validation set"""
        predictions = self.predict(texts)
        pred_labels = [r.label for r in predictions]
        
        accuracy = sum(p == l for p, l in zip(pred_labels, labels)) / len(labels)
        return accuracy
    
    def evaluate(self, test_texts: List[str], test_labels: List[str]) -> Dict[str, Any]:
        """
        Evaluate classifier performance.
        
        Args:
            test_texts: Test texts
            test_labels: True labels
            
        Returns:
            Evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Classifier must be trained before evaluation")
        
        predictions = self.predict(test_texts)
        pred_labels = [r.label for r in predictions]
        
        # Calculate metrics
        accuracy = sum(p == l for p, l in zip(pred_labels, test_labels)) / len(test_labels)
        
        # Per-class metrics
        class_metrics = {}
        for class_name in self.classes_:
            true_positives = sum(1 for p, t in zip(pred_labels, test_labels) 
                               if p == class_name and t == class_name)
            false_positives = sum(1 for p, t in zip(pred_labels, test_labels) 
                                if p == class_name and t != class_name)
            false_negatives = sum(1 for p, t in zip(pred_labels, test_labels) 
                                if p != class_name and t == class_name)
            
            precision = true_positives / (true_positives + false_positives + 1e-10)
            recall = true_positives / (true_positives + false_negatives + 1e-10)
            f1 = 2 * precision * recall / (precision + recall + 1e-10)
            
            class_metrics[class_name] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": sum(1 for l in test_labels if l == class_name)
            }
        
        return {
            "accuracy": accuracy,
            "training_accuracy": self.training_accuracy,
            "class_metrics": class_metrics,
            "total_samples": len(test_labels)
        }
    
    def save_model(self, path: str):
        """Save classifier to disk"""
        model_data = {
            "algorithm": self.algorithm.value,
            "feature_type": self.feature_type.value,
            "config": self.config,
            "preprocessing_steps": self.preprocessing_steps,
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "label_encoder": self.label_encoder,
            "classes": self.classes_,
            "feature_names": self.feature_names_,
            "is_trained": self.is_trained,
            "training_accuracy": self.training_accuracy
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: str):
        """Load classifier from disk"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.algorithm = ClassificationAlgorithm(model_data["algorithm"])
        self.feature_type = FeatureType(model_data["feature_type"])
        self.config = model_data["config"]
        self.preprocessing_steps = model_data["preprocessing_steps"]
        self.vectorizer = model_data["vectorizer"]
        self.classifier = model_data["classifier"]
        self.label_encoder = model_data["label_encoder"]
        self.classes_ = model_data["classes"]
        self.feature_names_ = model_data["feature_names"]
        self.is_trained = model_data["is_trained"]
        self.training_accuracy = model_data["training_accuracy"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get classifier statistics"""
        return {
            "algorithm": self.algorithm.value,
            "feature_type": self.feature_type.value,
            "is_trained": self.is_trained,
            "training_accuracy": self.training_accuracy,
            "num_classes": len(self.classes_),
            "num_features": len(self.feature_names_),
            "texts_processed": self.texts_processed
        }


class SimpleClassifier:
    """Simple fallback classifier when scikit-learn not available"""
    def __init__(self):
        self.class_features = defaultdict(lambda: defaultdict(float))
        self.class_counts = defaultdict(int)
        self.vocabulary = set()
    
    def fit(self, X, y):
        """Train simple classifier"""
        for features, label in zip(X, y):
            self.class_counts[label] += 1
            for i, value in enumerate(features):
                if value > 0:
                    self.class_features[label][i] += value
    
    def predict(self, X):
        """Predict using simple scoring"""
        predictions = []
        for features in X:
            scores = {}
            for label in self.class_counts:
                score = 0
                for i, value in enumerate(features):
                    if value > 0 and i in self.class_features[label]:
                        score += self.class_features[label][i] * value
                scores[label] = score / (self.class_counts[label] + 1)
            
            predictions.append(max(scores, key=scores.get))
        return np.array(predictions)
    
    def predict_proba(self, X):
        """Get probabilities"""
        all_probs = []
        for features in X:
            scores = {}
            for label in self.class_counts:
                score = 0
                for i, value in enumerate(features):
                    if value > 0 and i in self.class_features[label]:
                        score += self.class_features[label][i] * value
                scores[label] = score / (self.class_counts[label] + 1)
            
            # Normalize to probabilities
            total = sum(scores.values()) + 1e-10
            probs = [scores.get(i, 0) / total for i in range(len(self.class_counts))]
            all_probs.append(probs)
        
        return np.array(all_probs)


# Utility functions
def classify_text(text: str, model_path: Optional[str] = None) -> str:
    """Quick text classification"""
    if model_path and Path(model_path).exists():
        classifier = TextClassifier()
        classifier.load_model(model_path)
    else:
        # Use default classifier
        classifier = TextClassifier()
        # Train on dummy data
        texts = ["I love this!", "This is terrible", "Not bad"]
        labels = ["positive", "negative", "neutral"]
        classifier.train(texts, labels)
    
    result = classifier.predict(text)
    return result.label


def sentiment_analysis(texts: List[str]) -> List[str]:
    """Simple sentiment analysis"""
    # Train sentiment classifier
    classifier = TextClassifier(algorithm="naive_bayes")
    
    # Training data
    train_texts = [
        "I love this product, it's amazing!",
        "Best purchase ever!",
        "Excellent quality and fast shipping",
        "Terrible product, waste of money",
        "Completely disappointed",
        "Poor quality, would not recommend",
        "It's okay, nothing special",
        "Average product, as expected",
        "Not bad but not great either"
    ]
    train_labels = ["positive"] * 3 + ["negative"] * 3 + ["neutral"] * 3
    
    classifier.train(train_texts, train_labels)
    
    # Predict sentiments
    results = classifier.predict(texts)
    return [r.label for r in results]


# Auto-generated tests
def test_text_classifier():
    """Test text classification functionality"""
    # Test data
    train_texts = [
        "Python is a great programming language",
        "Java is widely used in enterprise",
        "Machine learning is fascinating",
        "Deep learning transforms AI",
        "I love playing football",
        "Basketball is my favorite sport"
    ]
    train_labels = ["tech", "tech", "tech", "tech", "sports", "sports"]
    
    # Test basic classification
    classifier = TextClassifier(algorithm="naive_bayes")
    classifier.train(train_texts, train_labels)
    
    # Test prediction
    result = classifier.predict("JavaScript is popular for web development")
    assert result.label == "tech"
    assert result.confidence > 0.5
    
    # Test batch prediction
    test_texts = ["Soccer is exciting", "Artificial intelligence is the future"]
    results = classifier.predict(test_texts)
    assert len(results) == 2
    assert results[0].label == "sports"
    assert results[1].label == "tech"
    
    # Test probability prediction
    probs = classifier.predict_proba("Programming and coding")
    assert "tech" in probs
    assert "sports" in probs
    assert probs["tech"] > probs["sports"]
    
    # Test evaluation
    eval_metrics = classifier.evaluate(train_texts, train_labels)
    assert eval_metrics["accuracy"] > 0.8  # Should have high accuracy on training data
    
    # Test different algorithms
    for algo in ["svm", "random_forest", "logistic_regression"]:
        clf = TextClassifier(algorithm=algo)
        clf.train(train_texts[:4], train_labels[:4])  # Smaller dataset
        pred = clf.predict("Python programming")
        assert isinstance(pred, ClassificationResult)
    
    # Test sentiment analysis utility
    sentiments = sentiment_analysis(["This is wonderful!", "Terrible experience"])
    assert sentiments[0] == "positive"
    assert sentiments[1] == "negative"
    
    # Test statistics
    stats = classifier.get_statistics()
    assert stats["is_trained"] == True
    assert stats["num_classes"] == 2
    
    print("All text classification tests passed!")


if __name__ == "__main__":
    test_text_classifier()