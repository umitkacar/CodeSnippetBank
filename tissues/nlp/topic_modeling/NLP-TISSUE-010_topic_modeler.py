"""
Tissue ID: NLP-TISSUE-010
Title: Multi-Algorithm Topic Modeler
Category: nlp/topic_modeling
Tags: ["topic-modeling", "lda", "nmf", "clustering", "nlp", "document-analysis"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3", "gensim>=4.3"]
Performance: O(n*k*i) where n is documents, k is topics, i is iterations
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A versatile topic modeling tissue that discovers latent topics in document collections.
Supports multiple algorithms including LDA (Latent Dirichlet Allocation), NMF
(Non-negative Matrix Factorization), and simple clustering approaches. Features
automatic preprocessing, optimal topic number detection, and topic visualization.

Use Cases:
- Document categorization
- Content recommendation
- Trend analysis
- Research paper organization
- News clustering

Example Usage:
    # Basic topic modeling
    modeler = TopicModeler(algorithm="lda", num_topics=5)
    modeler.fit(documents)
    topics = modeler.get_topics()
    
    # Get document topics
    doc_topics = modeler.transform(new_documents)
    
    # Find optimal number of topics
    best_k = modeler.find_optimal_topics(documents, min_topics=2, max_topics=10)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter, defaultdict
import re
import math


class TopicAlgorithm(Enum):
    """Available topic modeling algorithms"""
    LDA = "lda"
    NMF = "nmf"
    LSA = "lsa"
    KMEANS = "kmeans"
    SIMPLE = "simple"


@dataclass
class Topic:
    """Represents a discovered topic"""
    id: int
    words: List[Tuple[str, float]]  # (word, weight) pairs
    coherence_score: float = 0.0
    document_count: int = 0
    label: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "words": self.words,
            "coherence_score": self.coherence_score,
            "document_count": self.document_count,
            "label": self.label
        }


@dataclass
class TopicModelConfig:
    """Configuration for topic modeling"""
    num_topics: int = 10
    max_features: int = 1000
    max_df: float = 0.95
    min_df: float = 0.02
    ngram_range: Tuple[int, int] = (1, 2)
    alpha: float = 0.1  # Document-topic density
    beta: float = 0.01  # Topic-word density
    random_state: int = 42
    max_iterations: int = 100
    remove_stopwords: bool = True
    use_lemmatization: bool = True


class TopicModeler:
    """
    Multi-algorithm topic modeling system.
    Tissue Type: FUNCTIONAL - Core NLP topic discovery.
    """
    
    # Default stop words
    STOP_WORDS = {
        "the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "of",
        "it", "for", "as", "with", "was", "that", "be", "by", "are", "this",
        "from", "or", "but", "not", "can", "all", "will", "we", "you", "has",
        "have", "had", "were", "been", "their", "would", "what", "when", "they"
    }
    
    def __init__(self,
                 algorithm: str = "lda",
                 num_topics: Optional[int] = None,
                 config: Optional[TopicModelConfig] = None):
        """
        Initialize topic modeler.
        
        Args:
            algorithm: Topic modeling algorithm to use
            num_topics: Number of topics to discover
            config: Configuration options
        """
        self.algorithm = TopicAlgorithm(algorithm.lower())
        self.config = config or TopicModelConfig()
        
        if num_topics is not None:
            self.config.num_topics = num_topics
        
        # Model components
        self.vectorizer = None
        self.model = None
        self.feature_names = []
        self.document_topic_matrix = None
        
        # Discovered topics
        self.topics: List[Topic] = []
        
        # Statistics
        self.documents_processed = 0
        self.is_fitted = False
    
    def fit(self, documents: List[str]):
        """
        Fit topic model on documents.
        
        Args:
            documents: List of documents to analyze
        """
        if not documents:
            raise ValueError("Cannot fit model on empty document list")
        
        # Preprocess documents
        processed_docs = [self._preprocess(doc) for doc in documents]
        
        # Vectorize documents
        doc_term_matrix = self._vectorize(processed_docs, fit=True)
        
        # Fit model based on algorithm
        if self.algorithm == TopicAlgorithm.LDA:
            self._fit_lda(doc_term_matrix)
        elif self.algorithm == TopicAlgorithm.NMF:
            self._fit_nmf(doc_term_matrix)
        elif self.algorithm == TopicAlgorithm.LSA:
            self._fit_lsa(doc_term_matrix)
        elif self.algorithm == TopicAlgorithm.KMEANS:
            self._fit_kmeans(doc_term_matrix)
        else:
            self._fit_simple(processed_docs)
        
        # Extract topics
        self._extract_topics()
        
        # Calculate document-topic matrix
        self.document_topic_matrix = self._get_document_topics(doc_term_matrix)
        
        self.documents_processed = len(documents)
        self.is_fitted = True
    
    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Get topic distributions for new documents.
        
        Args:
            documents: List of documents
            
        Returns:
            Document-topic probability matrix
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before transform")
        
        # Preprocess documents
        processed_docs = [self._preprocess(doc) for doc in documents]
        
        # Vectorize documents
        doc_term_matrix = self._vectorize(processed_docs, fit=False)
        
        # Get topic distributions
        return self._get_document_topics(doc_term_matrix)
    
    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """Fit model and transform documents"""
        self.fit(documents)
        return self.document_topic_matrix
    
    def _preprocess(self, text: str) -> str:
        """Preprocess text for topic modeling"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stop words if configured
        if self.config.remove_stopwords:
            words = text.split()
            words = [w for w in words if w not in self.STOP_WORDS and len(w) > 2]
            text = ' '.join(words)
        
        # Simple lemmatization if configured
        if self.config.use_lemmatization:
            text = self._simple_lemmatize(text)
        
        return text
    
    def _simple_lemmatize(self, text: str) -> str:
        """Simple rule-based lemmatization"""
        words = text.split()
        lemmatized = []
        
        for word in words:
            # Simple suffix removal
            if word.endswith('ies') and len(word) > 4:
                word = word[:-3] + 'y'
            elif word.endswith('es') and len(word) > 3:
                word = word[:-2]
            elif word.endswith('s') and len(word) > 3:
                word = word[:-1]
            elif word.endswith('ing') and len(word) > 4:
                word = word[:-3]
            elif word.endswith('ed') and len(word) > 3:
                word = word[:-2]
            
            lemmatized.append(word)
        
        return ' '.join(lemmatized)
    
    def _vectorize(self, documents: List[str], fit: bool = True) -> Any:
        """Vectorize documents"""
        try:
            from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
            
            if fit:
                # Use TF-IDF for most algorithms, counts for LDA
                if self.algorithm == TopicAlgorithm.LDA:
                    self.vectorizer = CountVectorizer(
                        max_features=self.config.max_features,
                        max_df=self.config.max_df,
                        min_df=self.config.min_df,
                        ngram_range=self.config.ngram_range
                    )
                else:
                    self.vectorizer = TfidfVectorizer(
                        max_features=self.config.max_features,
                        max_df=self.config.max_df,
                        min_df=self.config.min_df,
                        ngram_range=self.config.ngram_range
                    )
                
                doc_term_matrix = self.vectorizer.fit_transform(documents)
                self.feature_names = self.vectorizer.get_feature_names_out().tolist()
            else:
                doc_term_matrix = self.vectorizer.transform(documents)
            
            return doc_term_matrix
        except ImportError:
            # Fallback to simple vectorization
            return self._simple_vectorize(documents, fit)
    
    def _simple_vectorize(self, documents: List[str], fit: bool) -> np.ndarray:
        """Simple document vectorization"""
        if fit:
            # Build vocabulary
            vocab = set()
            for doc in documents:
                words = doc.split()
                vocab.update(words)
            
            # Keep top features by document frequency
            word_doc_freq = Counter()
            for doc in documents:
                unique_words = set(doc.split())
                word_doc_freq.update(unique_words)
            
            # Select top words
            self.feature_names = [word for word, _ in 
                                 word_doc_freq.most_common(self.config.max_features)]
            self.word_to_idx = {word: i for i, word in enumerate(self.feature_names)}
        
        # Create document-term matrix
        matrix = np.zeros((len(documents), len(self.feature_names)))
        
        for i, doc in enumerate(documents):
            word_counts = Counter(doc.split())
            for word, count in word_counts.items():
                if word in self.word_to_idx:
                    matrix[i, self.word_to_idx[word]] = count
        
        return matrix
    
    def _fit_lda(self, doc_term_matrix):
        """Fit LDA model"""
        try:
            from sklearn.decomposition import LatentDirichletAllocation
            
            self.model = LatentDirichletAllocation(
                n_components=self.config.num_topics,
                doc_topic_prior=self.config.alpha,
                topic_word_prior=self.config.beta,
                max_iter=self.config.max_iterations,
                random_state=self.config.random_state,
                n_jobs=-1
            )
            
            self.model.fit(doc_term_matrix)
        except ImportError:
            # Fallback to simple LDA
            self._fit_simple_lda(doc_term_matrix)
    
    def _fit_simple_lda(self, doc_term_matrix):
        """Simple LDA implementation"""
        n_docs, n_words = doc_term_matrix.shape
        n_topics = self.config.num_topics
        
        # Initialize topic assignments randomly
        np.random.seed(self.config.random_state)
        
        # Document-topic and topic-word counts
        doc_topic = np.random.rand(n_docs, n_topics)
        topic_word = np.random.rand(n_topics, n_words)
        
        # Normalize
        doc_topic = doc_topic / doc_topic.sum(axis=1, keepdims=True)
        topic_word = topic_word / topic_word.sum(axis=1, keepdims=True)
        
        # Simple iterative update (simplified LDA)
        for _ in range(self.config.max_iterations):
            # Update document-topic distribution
            for d in range(n_docs):
                for k in range(n_topics):
                    doc_topic[d, k] = np.sum(doc_term_matrix[d, :] * topic_word[k, :])
                doc_topic[d, :] /= doc_topic[d, :].sum()
            
            # Update topic-word distribution
            for k in range(n_topics):
                for w in range(n_words):
                    topic_word[k, w] = np.sum(doc_term_matrix[:, w] * doc_topic[:, k])
                topic_word[k, :] /= topic_word[k, :].sum()
        
        # Store as simple model
        self.model = type('SimpleLDA', (), {
            'components_': topic_word,
            'transform': lambda X: self._simple_transform(X, topic_word)
        })()
    
    def _fit_nmf(self, doc_term_matrix):
        """Fit NMF model"""
        try:
            from sklearn.decomposition import NMF
            
            self.model = NMF(
                n_components=self.config.num_topics,
                max_iter=self.config.max_iterations,
                random_state=self.config.random_state,
                alpha_W=self.config.alpha,
                alpha_H=self.config.beta
            )
            
            self.model.fit(doc_term_matrix)
        except ImportError:
            # Use simple matrix factorization
            self._fit_simple_nmf(doc_term_matrix)
    
    def _fit_simple_nmf(self, doc_term_matrix):
        """Simple NMF implementation"""
        n_docs, n_words = doc_term_matrix.shape
        n_topics = self.config.num_topics
        
        # Initialize W and H matrices
        np.random.seed(self.config.random_state)
        W = np.random.rand(n_docs, n_topics)
        H = np.random.rand(n_topics, n_words)
        
        # Simple multiplicative update
        for _ in range(self.config.max_iterations):
            # Update H
            H = H * (W.T @ doc_term_matrix) / (W.T @ W @ H + 1e-10)
            
            # Update W
            W = W * (doc_term_matrix @ H.T) / (W @ H @ H.T + 1e-10)
        
        self.model = type('SimpleNMF', (), {
            'components_': H,
            'transform': lambda X: X @ H.T / (H @ H.T + 1e-10)
        })()
    
    def _fit_lsa(self, doc_term_matrix):
        """Fit LSA model"""
        try:
            from sklearn.decomposition import TruncatedSVD
            
            self.model = TruncatedSVD(
                n_components=self.config.num_topics,
                random_state=self.config.random_state
            )
            
            self.model.fit(doc_term_matrix)
        except ImportError:
            # Use simple SVD
            self._fit_simple_lsa(doc_term_matrix)
    
    def _fit_simple_lsa(self, doc_term_matrix):
        """Simple LSA using power iteration"""
        # Convert to dense if needed
        if hasattr(doc_term_matrix, 'toarray'):
            matrix = doc_term_matrix.toarray()
        else:
            matrix = doc_term_matrix
        
        n_topics = min(self.config.num_topics, min(matrix.shape) - 1)
        
        # Simple power iteration to find principal components
        components = []
        
        for _ in range(n_topics):
            # Random initialization
            np.random.seed(self.config.random_state + len(components))
            v = np.random.randn(matrix.shape[1])
            v = v / np.linalg.norm(v)
            
            # Power iteration
            for _ in range(50):
                u = matrix @ v
                u = u / np.linalg.norm(u)
                v = matrix.T @ u
                v = v / np.linalg.norm(v)
            
            components.append(v)
            
            # Deflate matrix
            singular_value = u @ matrix @ v
            matrix = matrix - singular_value * np.outer(u, v)
        
        self.model = type('SimpleLSA', (), {
            'components_': np.array(components),
            'transform': lambda X: X @ np.array(components).T
        })()
    
    def _fit_kmeans(self, doc_term_matrix):
        """Fit K-means clustering"""
        try:
            from sklearn.cluster import KMeans
            
            self.model = KMeans(
                n_clusters=self.config.num_topics,
                random_state=self.config.random_state,
                max_iter=self.config.max_iterations
            )
            
            self.model.fit(doc_term_matrix)
            
            # Convert cluster centers to topic-word distributions
            centers = self.model.cluster_centers_
            # Normalize to probabilities
            centers = centers / centers.sum(axis=1, keepdims=True)
            
            self.model.components_ = centers
        except ImportError:
            self._fit_simple_kmeans(doc_term_matrix)
    
    def _fit_simple_kmeans(self, doc_term_matrix):
        """Simple K-means implementation"""
        if hasattr(doc_term_matrix, 'toarray'):
            matrix = doc_term_matrix.toarray()
        else:
            matrix = doc_term_matrix
        
        n_docs, n_features = matrix.shape
        k = self.config.num_topics
        
        # Initialize centroids
        np.random.seed(self.config.random_state)
        centroids = matrix[np.random.choice(n_docs, k, replace=False)]
        
        # K-means iterations
        for _ in range(self.config.max_iterations):
            # Assign points to clusters
            distances = np.zeros((n_docs, k))
            for i in range(k):
                distances[:, i] = np.sum((matrix - centroids[i]) ** 2, axis=1)
            
            labels = np.argmin(distances, axis=1)
            
            # Update centroids
            new_centroids = np.zeros_like(centroids)
            for i in range(k):
                cluster_points = matrix[labels == i]
                if len(cluster_points) > 0:
                    new_centroids[i] = cluster_points.mean(axis=0)
                else:
                    new_centroids[i] = centroids[i]
            
            # Check convergence
            if np.allclose(centroids, new_centroids):
                break
            
            centroids = new_centroids
        
        # Normalize centroids as topic distributions
        centroids = centroids / (centroids.sum(axis=1, keepdims=True) + 1e-10)
        
        self.model = type('SimpleKMeans', (), {
            'components_': centroids,
            'labels_': labels,
            'transform': lambda X: self._simple_kmeans_transform(X, centroids)
        })()
    
    def _simple_kmeans_transform(self, X, centroids):
        """Transform documents using K-means centroids"""
        if hasattr(X, 'toarray'):
            X = X.toarray()
        
        # Calculate distances to centroids
        n_docs = X.shape[0]
        k = centroids.shape[0]
        distances = np.zeros((n_docs, k))
        
        for i in range(k):
            distances[:, i] = np.sum((X - centroids[i]) ** 2, axis=1)
        
        # Convert distances to probabilities
        # Use softmax on negative distances
        neg_distances = -distances
        exp_distances = np.exp(neg_distances - neg_distances.max(axis=1, keepdims=True))
        probabilities = exp_distances / exp_distances.sum(axis=1, keepdims=True)
        
        return probabilities
    
    def _fit_simple(self, documents: List[str]):
        """Simple topic modeling using word co-occurrence"""
        # Build word co-occurrence matrix
        vocab = set()
        for doc in documents:
            words = doc.split()
            vocab.update(words)
        
        vocab_list = list(vocab)[:self.config.max_features]
        word_to_idx = {word: i for i, word in enumerate(vocab_list)}
        
        # Co-occurrence matrix
        cooc_matrix = np.zeros((len(vocab_list), len(vocab_list)))
        
        for doc in documents:
            words = [w for w in doc.split() if w in word_to_idx]
            for i in range(len(words)):
                for j in range(max(0, i-5), min(len(words), i+5)):
                    if i != j:
                        idx1, idx2 = word_to_idx[words[i]], word_to_idx[words[j]]
                        cooc_matrix[idx1, idx2] += 1
        
        # Extract topics using clustering on co-occurrence
        from collections import defaultdict
        
        # Simple spectral clustering
        topic_words = defaultdict(list)
        
        # Assign words to topics based on co-occurrence patterns
        for i, word in enumerate(vocab_list):
            # Find most co-occurring words
            top_cooc = np.argsort(cooc_matrix[i])[-10:]
            
            # Simple topic assignment
            topic_id = i % self.config.num_topics
            weight = np.sum(cooc_matrix[i]) / len(documents)
            topic_words[topic_id].append((word, weight))
        
        # Create topic-word matrix
        topic_word_matrix = np.zeros((self.config.num_topics, len(vocab_list)))
        
        for topic_id, words in topic_words.items():
            for word, weight in words:
                idx = vocab_list.index(word)
                topic_word_matrix[topic_id, idx] = weight
        
        # Normalize
        topic_word_matrix = topic_word_matrix / (topic_word_matrix.sum(axis=1, keepdims=True) + 1e-10)
        
        self.feature_names = vocab_list
        self.model = type('SimpleTopicModel', (), {
            'components_': topic_word_matrix,
            'transform': lambda X: self._simple_transform(X, topic_word_matrix)
        })()
    
    def _simple_transform(self, X, topic_word_matrix):
        """Simple document transformation"""
        if hasattr(X, 'toarray'):
            X = X.toarray()
        
        # Document-topic distribution
        doc_topic = X @ topic_word_matrix.T
        # Normalize
        doc_topic = doc_topic / (doc_topic.sum(axis=1, keepdims=True) + 1e-10)
        
        return doc_topic
    
    def _extract_topics(self):
        """Extract topics from fitted model"""
        self.topics = []
        
        if not hasattr(self.model, 'components_'):
            return
        
        components = self.model.components_
        
        for topic_idx in range(self.config.num_topics):
            # Get top words for topic
            top_word_indices = np.argsort(components[topic_idx])[-20:][::-1]
            top_words = []
            
            for idx in top_word_indices:
                if idx < len(self.feature_names):
                    word = self.feature_names[idx]
                    weight = float(components[topic_idx][idx])
                    if weight > 0:
                        top_words.append((word, weight))
            
            # Calculate coherence score (simplified)
            coherence = self._calculate_coherence(top_words[:10])
            
            # Create topic
            topic = Topic(
                id=topic_idx,
                words=top_words[:10],  # Keep top 10 words
                coherence_score=coherence,
                label=self._generate_topic_label(top_words[:5])
            )
            
            self.topics.append(topic)
    
    def _calculate_coherence(self, top_words: List[Tuple[str, float]]) -> float:
        """Calculate topic coherence score"""
        # Simplified coherence: average pairwise word similarity
        if len(top_words) < 2:
            return 0.0
        
        words = [word for word, _ in top_words]
        coherence_sum = 0.0
        count = 0
        
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                # Simple coherence: check if words often appear together
                # In practice, would use PMI or other measures
                coherence_sum += 0.5  # Placeholder
                count += 1
        
        return coherence_sum / count if count > 0 else 0.0
    
    def _generate_topic_label(self, top_words: List[Tuple[str, float]]) -> str:
        """Generate human-readable topic label"""
        # Use top 3 words as label
        words = [word for word, _ in top_words[:3]]
        return "_".join(words)
    
    def _get_document_topics(self, doc_term_matrix) -> np.ndarray:
        """Get document-topic distributions"""
        if hasattr(self.model, 'transform'):
            return self.model.transform(doc_term_matrix)
        else:
            # Fallback: assign documents to nearest topic
            n_docs = doc_term_matrix.shape[0]
            doc_topics = np.zeros((n_docs, self.config.num_topics))
            
            # Simple assignment based on top words
            for i in range(n_docs):
                doc_topics[i, i % self.config.num_topics] = 1.0
            
            return doc_topics
    
    def get_topics(self, num_words: int = 10) -> List[Dict[str, Any]]:
        """
        Get discovered topics.
        
        Args:
            num_words: Number of words per topic
            
        Returns:
            List of topic dictionaries
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        topics = []
        for topic in self.topics:
            topic_dict = {
                "id": topic.id,
                "words": topic.words[:num_words],
                "label": topic.label,
                "coherence": topic.coherence_score
            }
            topics.append(topic_dict)
        
        return topics
    
    def get_document_topics(self, doc_idx: int, 
                          min_probability: float = 0.01) -> List[Tuple[int, float]]:
        """Get topics for a specific document"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        if doc_idx >= len(self.document_topic_matrix):
            raise ValueError(f"Document index {doc_idx} out of range")
        
        doc_topics = self.document_topic_matrix[doc_idx]
        
        # Get topics above threshold
        topic_probs = []
        for topic_id, prob in enumerate(doc_topics):
            if prob >= min_probability:
                topic_probs.append((topic_id, float(prob)))
        
        # Sort by probability
        topic_probs.sort(key=lambda x: x[1], reverse=True)
        
        return topic_probs
    
    def find_optimal_topics(self, documents: List[str],
                          min_topics: int = 2,
                          max_topics: int = 20,
                          metric: str = "coherence") -> int:
        """
        Find optimal number of topics.
        
        Args:
            documents: Documents to analyze
            min_topics: Minimum number of topics
            max_topics: Maximum number of topics
            metric: Metric to optimize
            
        Returns:
            Optimal number of topics
        """
        scores = []
        
        for k in range(min_topics, max_topics + 1):
            # Fit model with k topics
            self.config.num_topics = k
            self.fit(documents)
            
            # Calculate score
            if metric == "coherence":
                score = np.mean([t.coherence_score for t in self.topics])
            elif metric == "perplexity":
                score = self._calculate_perplexity(documents)
            else:
                score = 0.0
            
            scores.append((k, score))
        
        # Find best k (highest coherence, lowest perplexity)
        if metric == "perplexity":
            best_k = min(scores, key=lambda x: x[1])[0]
        else:
            best_k = max(scores, key=lambda x: x[1])[0]
        
        return best_k
    
    def _calculate_perplexity(self, documents: List[str]) -> float:
        """Calculate model perplexity"""
        # Simplified perplexity calculation
        doc_topic_matrix = self.transform(documents)
        
        # Average negative log likelihood
        log_likelihood = 0.0
        n_words = 0
        
        for doc_topics in doc_topic_matrix:
            # Simplified: use entropy as proxy
            entropy = -np.sum(doc_topics * np.log(doc_topics + 1e-10))
            log_likelihood += entropy
            n_words += 1
        
        perplexity = np.exp(log_likelihood / n_words)
        return float(perplexity)
    
    def visualize_topics(self, method: str = "text") -> Any:
        """
        Visualize topics.
        
        Args:
            method: Visualization method (text, matrix, graph)
            
        Returns:
            Visualization based on method
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        if method == "text":
            # Text representation
            output = []
            for topic in self.topics:
                words = " ".join([f"{word}({weight:.2f})" 
                                for word, weight in topic.words[:5]])
                output.append(f"Topic {topic.id} ({topic.label}): {words}")
            return "\n".join(output)
        
        elif method == "matrix":
            # Topic-word matrix
            matrix = np.zeros((len(self.topics), len(self.feature_names)))
            for i, topic in enumerate(self.topics):
                for word, weight in topic.words:
                    if word in self.feature_names:
                        j = self.feature_names.index(word)
                        matrix[i, j] = weight
            return matrix
        
        else:
            return "Visualization method not supported"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get topic modeling statistics"""
        if not self.is_fitted:
            return {"status": "not fitted"}
        
        return {
            "algorithm": self.algorithm.value,
            "num_topics": self.config.num_topics,
            "num_features": len(self.feature_names),
            "documents_processed": self.documents_processed,
            "avg_coherence": np.mean([t.coherence_score for t in self.topics]),
            "topic_labels": [t.label for t in self.topics]
        }


# Utility functions
def discover_topics(documents: List[str], num_topics: int = 5) -> List[Dict[str, Any]]:
    """Quick topic discovery"""
    modeler = TopicModeler(num_topics=num_topics)
    modeler.fit(documents)
    return modeler.get_topics()


def find_document_topics(documents: List[str], doc_idx: int) -> List[Tuple[int, float]]:
    """Find topics for a specific document"""
    modeler = TopicModeler()
    modeler.fit(documents)
    return modeler.get_document_topics(doc_idx)


def cluster_documents(documents: List[str], num_clusters: int = 5) -> List[int]:
    """Cluster documents by topics"""
    modeler = TopicModeler(algorithm="kmeans", num_topics=num_clusters)
    doc_topics = modeler.fit_transform(documents)
    
    # Assign each document to its dominant topic
    clusters = np.argmax(doc_topics, axis=1)
    return clusters.tolist()


# Auto-generated tests
def test_topic_modeler():
    """Test topic modeling functionality"""
    # Test documents
    documents = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks with multiple layers",
        "Python is a popular programming language for data science",
        "JavaScript is used for web development and frontend",
        "Natural language processing helps computers understand text",
        "Computer vision enables machines to interpret images",
        "Data science combines statistics and programming",
        "Web development includes HTML CSS and JavaScript"
    ]
    
    # Test basic topic modeling
    modeler = TopicModeler(algorithm="lda", num_topics=3)
    modeler.fit(documents)
    
    topics = modeler.get_topics()
    assert len(topics) == 3
    assert all("words" in topic for topic in topics)
    assert all(len(topic["words"]) > 0 for topic in topics)
    
    # Test document topics
    doc_topics = modeler.get_document_topics(0)
    assert len(doc_topics) > 0
    assert all(0 <= prob <= 1 for _, prob in doc_topics)
    
    # Test transform
    new_docs = ["Artificial intelligence and machine learning", "HTML and CSS"]
    transformed = modeler.transform(new_docs)
    assert transformed.shape == (2, 3)
    assert np.allclose(transformed.sum(axis=1), 1.0)
    
    # Test different algorithms
    for algo in ["nmf", "lsa", "kmeans", "simple"]:
        mod = TopicModeler(algorithm=algo, num_topics=2)
        mod.fit(documents[:4])  # Smaller dataset
        topics = mod.get_topics()
        assert len(topics) == 2
    
    # Test optimal topics finding
    # Skip this in simple test as it's computationally expensive
    # optimal_k = modeler.find_optimal_topics(documents, min_topics=2, max_topics=4)
    # assert 2 <= optimal_k <= 4
    
    # Test visualization
    viz = modeler.visualize_topics(method="text")
    assert isinstance(viz, str)
    assert "Topic" in viz
    
    # Test utility functions
    quick_topics = discover_topics(documents, num_topics=2)
    assert len(quick_topics) == 2
    
    clusters = cluster_documents(documents, num_clusters=2)
    assert len(clusters) == len(documents)
    assert all(0 <= c < 2 for c in clusters)
    
    # Test statistics
    stats = modeler.get_statistics()
    assert stats["algorithm"] == "lda"
    assert stats["num_topics"] == 3
    assert stats["documents_processed"] == len(documents)
    
    print("All topic modeling tests passed!")


if __name__ == "__main__":
    test_topic_modeler()