"""
Tissue ID: NLP-TISSUE-004
Title: Multi-Strategy Sentence Embedder
Category: nlp/embeddings
Tags: ["embeddings", "sentence-embeddings", "vector-representation", "similarity", "nlp"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3", "sentence-transformers>=2.2"]
Performance: O(n*d) where n is number of sentences, d is embedding dimension
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive sentence embedding tissue that provides multiple strategies for
converting text into dense vector representations. Includes TF-IDF, Word2Vec
averaging, and transformer-based embeddings. Optimized for similarity search
and clustering tasks.

Use Cases:
- Semantic search and retrieval
- Document similarity computation
- Clustering and classification
- Question answering systems
- Duplicate detection

Example Usage:
    # Basic embedding
    embedder = SentenceEmbedder(strategy="tfidf")
    embeddings = embedder.embed(["Hello world", "Hi there"])
    
    # Similarity computation
    similarity = embedder.compute_similarity(embeddings[0], embeddings[1])
    
    # Advanced with pre-trained models
    embedder = SentenceEmbedder(strategy="transformer", model_name="all-MiniLM-L6-v2")
    embeddings = embedder.embed_batch(sentences, batch_size=32)
"""

import numpy as np
from typing import List, Dict, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from pathlib import Path


class EmbeddingStrategy(Enum):
    """Available embedding strategies"""
    TFIDF = "tfidf"
    WORD_AVG = "word_avg"
    TRANSFORMER = "transformer"
    USE = "universal_sentence_encoder"
    CUSTOM = "custom"


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation"""
    normalize: bool = True
    lowercase: bool = True
    remove_stopwords: bool = False
    max_sequence_length: int = 512
    embedding_dim: Optional[int] = None
    pooling_strategy: str = "mean"  # mean, max, cls
    cache_embeddings: bool = True
    device: str = "cpu"  # cpu, cuda, mps


class SentenceEmbedder:
    """
    Multi-strategy sentence embedder for vector representations.
    Tissue Type: FUNCTIONAL - Core NLP embedding functionality.
    """
    
    def __init__(self,
                 strategy: str = "tfidf",
                 model_name: Optional[str] = None,
                 config: Optional[EmbeddingConfig] = None):
        """
        Initialize sentence embedder.
        
        Args:
            strategy: Embedding strategy to use
            model_name: Pre-trained model name (for transformer strategy)
            config: Configuration options
        """
        self.strategy = EmbeddingStrategy(strategy.lower())
        self.model_name = model_name
        self.config = config or EmbeddingConfig()
        
        # Initialize model based on strategy
        self._init_model()
        
        # Cache for embeddings
        self.cache = {} if self.config.cache_embeddings else None
        
        # Statistics
        self.sentences_processed = 0
        self.cache_hits = 0
    
    def _init_model(self):
        """Initialize the embedding model"""
        if self.strategy == EmbeddingStrategy.TFIDF:
            self._init_tfidf()
        elif self.strategy == EmbeddingStrategy.WORD_AVG:
            self._init_word_avg()
        elif self.strategy == EmbeddingStrategy.TRANSFORMER:
            self._init_transformer()
        else:
            self.model = None
    
    def _init_tfidf(self):
        """Initialize TF-IDF model"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            self.model = TfidfVectorizer(
                lowercase=self.config.lowercase,
                max_features=self.config.embedding_dim or 1000,
                norm='l2' if self.config.normalize else None
            )
            self.fitted = False
        except ImportError:
            print("Warning: scikit-learn not available for TF-IDF")
            self.model = None
    
    def _init_word_avg(self):
        """Initialize word averaging model"""
        # Simple word embeddings dictionary
        self.word_embeddings = {}
        self.embedding_dim = self.config.embedding_dim or 300
        self.vocab_size = 0
        
        # In production, would load pre-trained embeddings
        # For now, use random embeddings
        self.model = "word_avg"
    
    def _init_transformer(self):
        """Initialize transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = self.model_name or "all-MiniLM-L6-v2"
            self.model = SentenceTransformer(model_name, device=self.config.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        except ImportError:
            print("Warning: sentence-transformers not available")
            self.model = None
    
    def embed(self, text: Union[str, List[str]]) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Embed text into vector representation.
        
        Args:
            text: Single sentence or list of sentences
            
        Returns:
            Embedding vector(s)
        """
        if isinstance(text, str):
            return self._embed_single(text)
        else:
            return self.embed_batch(text)
    
    def _embed_single(self, text: str) -> np.ndarray:
        """Embed a single sentence"""
        # Check cache
        if self.cache is not None and text in self.cache:
            self.cache_hits += 1
            return self.cache[text]
        
        # Generate embedding
        if self.strategy == EmbeddingStrategy.TFIDF:
            embedding = self._embed_tfidf([text])[0]
        elif self.strategy == EmbeddingStrategy.WORD_AVG:
            embedding = self._embed_word_avg(text)
        elif self.strategy == EmbeddingStrategy.TRANSFORMER:
            embedding = self._embed_transformer([text])[0]
        else:
            embedding = self._embed_custom(text)
        
        # Cache result
        if self.cache is not None:
            self.cache[text] = embedding
        
        self.sentences_processed += 1
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Embed multiple sentences in batches"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            if self.strategy == EmbeddingStrategy.TFIDF:
                batch_embeddings = self._embed_tfidf(batch)
            elif self.strategy == EmbeddingStrategy.WORD_AVG:
                batch_embeddings = [self._embed_word_avg(text) for text in batch]
            elif self.strategy == EmbeddingStrategy.TRANSFORMER:
                batch_embeddings = self._embed_transformer(batch)
            else:
                batch_embeddings = [self._embed_custom(text) for text in batch]
            
            embeddings.extend(batch_embeddings)
            self.sentences_processed += len(batch)
        
        return embeddings
    
    def _embed_tfidf(self, texts: List[str]) -> List[np.ndarray]:
        """TF-IDF embedding"""
        if self.model is None:
            return [np.zeros(100) for _ in texts]
        
        if not self.fitted:
            # Fit on current texts (in production, fit on larger corpus)
            self.model.fit(texts)
            self.fitted = True
        
        # Transform texts
        vectors = self.model.transform(texts)
        return [vectors[i].toarray().flatten() for i in range(vectors.shape[0])]
    
    def _embed_word_avg(self, text: str) -> np.ndarray:
        """Word averaging embedding"""
        # Simple tokenization
        words = text.lower().split() if self.config.lowercase else text.split()
        
        # Get word embeddings
        embeddings = []
        for word in words:
            if word not in self.word_embeddings:
                # Random embedding for unknown words
                self.word_embeddings[word] = np.random.randn(self.embedding_dim)
                self.vocab_size += 1
            embeddings.append(self.word_embeddings[word])
        
        if not embeddings:
            return np.zeros(self.embedding_dim)
        
        # Average embeddings
        if self.config.pooling_strategy == "mean":
            embedding = np.mean(embeddings, axis=0)
        elif self.config.pooling_strategy == "max":
            embedding = np.max(embeddings, axis=0)
        else:
            embedding = embeddings[0]  # CLS token
        
        # Normalize if requested
        if self.config.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
        
        return embedding
    
    def _embed_transformer(self, texts: List[str]) -> List[np.ndarray]:
        """Transformer-based embedding"""
        if self.model is None:
            return [np.zeros(384) for _ in texts]  # Default dimension
        
        # Encode sentences
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=self.config.normalize,
            show_progress_bar=False
        )
        
        return list(embeddings)
    
    def _embed_custom(self, text: str) -> np.ndarray:
        """Custom embedding logic"""
        # Placeholder for custom embeddings
        return np.random.randn(self.config.embedding_dim or 100)
    
    def compute_similarity(self, embedding1: np.ndarray, 
                         embedding2: np.ndarray,
                         metric: str = "cosine") -> float:
        """
        Compute similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            metric: Similarity metric (cosine, euclidean, dot)
            
        Returns:
            Similarity score
        """
        if metric == "cosine":
            # Cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm_product = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            return dot_product / norm_product if norm_product > 0 else 0.0
        elif metric == "euclidean":
            # Negative euclidean distance (higher is more similar)
            return -np.linalg.norm(embedding1 - embedding2)
        elif metric == "dot":
            # Dot product
            return np.dot(embedding1, embedding2)
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def find_similar(self, query_embedding: np.ndarray,
                    candidate_embeddings: List[np.ndarray],
                    top_k: int = 5,
                    metric: str = "cosine") -> List[Tuple[int, float]]:
        """
        Find most similar embeddings to query.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings
            top_k: Number of results to return
            metric: Similarity metric
            
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            sim = self.compute_similarity(query_embedding, candidate, metric)
            similarities.append((i, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def cluster_embeddings(self, embeddings: List[np.ndarray],
                          n_clusters: int = 5,
                          method: str = "kmeans") -> List[int]:
        """
        Cluster embeddings into groups.
        
        Args:
            embeddings: List of embedding vectors
            n_clusters: Number of clusters
            method: Clustering method
            
        Returns:
            Cluster assignments
        """
        try:
            from sklearn.cluster import KMeans, DBSCAN
            
            X = np.array(embeddings)
            
            if method == "kmeans":
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            elif method == "dbscan":
                clusterer = DBSCAN(eps=0.5, min_samples=2)
            else:
                raise ValueError(f"Unknown clustering method: {method}")
            
            labels = clusterer.fit_predict(X)
            return labels.tolist()
        except ImportError:
            print("Warning: scikit-learn not available for clustering")
            return list(range(len(embeddings)))
    
    def save_model(self, path: str):
        """Save embedding model to disk"""
        model_data = {
            "strategy": self.strategy.value,
            "model_name": self.model_name,
            "config": self.config,
            "vocab_size": getattr(self, "vocab_size", 0),
            "embedding_dim": getattr(self, "embedding_dim", None)
        }
        
        # Save model based on strategy
        if self.strategy == EmbeddingStrategy.TFIDF and self.fitted:
            model_data["tfidf_model"] = pickle.dumps(self.model)
        elif self.strategy == EmbeddingStrategy.WORD_AVG:
            model_data["word_embeddings"] = self.word_embeddings
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: str):
        """Load embedding model from disk"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.strategy = EmbeddingStrategy(model_data["strategy"])
        self.model_name = model_data.get("model_name")
        self.config = model_data.get("config", EmbeddingConfig())
        
        # Load model based on strategy
        if self.strategy == EmbeddingStrategy.TFIDF:
            self.model = pickle.loads(model_data.get("tfidf_model"))
            self.fitted = True
        elif self.strategy == EmbeddingStrategy.WORD_AVG:
            self.word_embeddings = model_data.get("word_embeddings", {})
            self.vocab_size = model_data.get("vocab_size", 0)
            self.embedding_dim = model_data.get("embedding_dim", 300)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get embedding statistics"""
        stats = {
            "strategy": self.strategy.value,
            "sentences_processed": self.sentences_processed,
            "cache_size": len(self.cache) if self.cache else 0,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": (self.cache_hits / self.sentences_processed * 100)
                            if self.sentences_processed > 0 else 0
        }
        
        if self.strategy == EmbeddingStrategy.WORD_AVG:
            stats["vocab_size"] = self.vocab_size
            stats["embedding_dim"] = self.embedding_dim
        elif self.strategy == EmbeddingStrategy.TRANSFORMER:
            stats["model_name"] = self.model_name
            stats["embedding_dim"] = getattr(self, "embedding_dim", None)
        
        return stats


# Utility functions
def embed_sentences(sentences: List[str], strategy: str = "tfidf") -> List[np.ndarray]:
    """Quick sentence embedding"""
    embedder = SentenceEmbedder(strategy=strategy)
    return embedder.embed_batch(sentences)


def compute_sentence_similarity(sent1: str, sent2: str, 
                              strategy: str = "transformer") -> float:
    """Compute similarity between two sentences"""
    embedder = SentenceEmbedder(strategy=strategy)
    emb1 = embedder.embed(sent1)
    emb2 = embedder.embed(sent2)
    return embedder.compute_similarity(emb1, emb2)


def semantic_search(query: str, documents: List[str], 
                   top_k: int = 5, strategy: str = "transformer") -> List[Tuple[int, float]]:
    """Perform semantic search over documents"""
    embedder = SentenceEmbedder(strategy=strategy)
    
    # Embed query and documents
    query_emb = embedder.embed(query)
    doc_embs = embedder.embed_batch(documents)
    
    # Find similar documents
    results = embedder.find_similar(query_emb, doc_embs, top_k=top_k)
    
    return results


# Auto-generated tests
def test_sentence_embedder():
    """Test sentence embedding functionality"""
    # Test TF-IDF embeddings
    embedder = SentenceEmbedder(strategy="tfidf")
    
    sentences = [
        "The quick brown fox jumps over the lazy dog",
        "A fast brown fox leaps over a sleepy dog",
        "Python is a great programming language",
        "Machine learning is fascinating"
    ]
    
    embeddings = embedder.embed_batch(sentences)
    assert len(embeddings) == len(sentences)
    assert all(isinstance(emb, np.ndarray) for emb in embeddings)
    
    # Test similarity
    sim1 = embedder.compute_similarity(embeddings[0], embeddings[1])
    sim2 = embedder.compute_similarity(embeddings[0], embeddings[2])
    assert sim1 > sim2  # First two sentences are more similar
    
    # Test word averaging
    embedder_avg = SentenceEmbedder(strategy="word_avg")
    emb = embedder_avg.embed("Hello world")
    assert isinstance(emb, np.ndarray)
    assert len(emb) == embedder_avg.embedding_dim
    
    # Test caching
    config = EmbeddingConfig(cache_embeddings=True)
    embedder_cached = SentenceEmbedder(strategy="word_avg", config=config)
    
    _ = embedder_cached.embed("Test sentence")
    _ = embedder_cached.embed("Test sentence")  # Should hit cache
    assert embedder_cached.cache_hits == 1
    
    # Test semantic search
    query = "programming with Python"
    results = semantic_search(query, sentences, top_k=2, strategy="tfidf")
    assert len(results) == 2
    assert results[0][0] == 2  # "Python is a great programming language"
    
    # Test clustering
    labels = embedder.cluster_embeddings(embeddings, n_clusters=2)
    assert len(labels) == len(embeddings)
    assert len(set(labels)) <= 2
    
    # Test statistics
    stats = embedder.get_statistics()
    assert stats["sentences_processed"] > 0
    
    print("All sentence embedding tests passed!")


if __name__ == "__main__":
    test_sentence_embedder()