"""
Text Embeddings
Generate and work with text embeddings for semantic search and similarity.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False


@dataclass
class EmbeddingResult:
    """Container for embedding results."""
    text: str
    embedding: np.ndarray
    model: str
    dimensions: int


class OpenAIEmbeddings:
    """Generate embeddings using OpenAI API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small"
    ):
        """
        Initialize OpenAI embeddings.

        Args:
            api_key: OpenAI API key
            model: Embedding model name
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for text.

        Args:
            text: Input text

        Returns:
            EmbeddingResult object
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )

        embedding = np.array(response.data[0].embedding)

        return EmbeddingResult(
            text=text,
            embedding=embedding,
            model=self.model,
            dimensions=len(embedding)
        )

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts
            batch_size: Batch size for API calls

        Returns:
            List of EmbeddingResult objects
        """
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )

            for text, data in zip(batch, response.data):
                embedding = np.array(data.embedding)
                results.append(EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    model=self.model,
                    dimensions=len(embedding)
                ))

        return results


class LocalEmbeddings:
    """Generate embeddings using local models (Sentence Transformers)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize local embeddings.

        Args:
            model_name: Sentence transformer model name
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")

        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding for text."""
        embedding = self.model.encode(text, convert_to_numpy=True)

        return EmbeddingResult(
            text=text,
            embedding=embedding,
            model=self.model_name,
            dimensions=len(embedding)
        )

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        return [
            EmbeddingResult(
                text=text,
                embedding=emb,
                model=self.model_name,
                dimensions=len(emb)
            )
            for text, emb in zip(texts, embeddings)
        ]


class CohereEmbeddings:
    """Generate embeddings using Cohere API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "embed-english-v3.0"
    ):
        """
        Initialize Cohere embeddings.

        Args:
            api_key: Cohere API key
            model: Embedding model name
        """
        if not COHERE_AVAILABLE:
            raise ImportError("cohere not installed")

        api_key = api_key or os.getenv("COHERE_API_KEY")
        self.client = cohere.Client(api_key)
        self.model = model

    def embed(self, text: str, input_type: str = "search_query") -> EmbeddingResult:
        """
        Generate embedding for text.

        Args:
            text: Input text
            input_type: "search_query" or "search_document"

        Returns:
            EmbeddingResult object
        """
        response = self.client.embed(
            texts=[text],
            model=self.model,
            input_type=input_type
        )

        embedding = np.array(response.embeddings[0])

        return EmbeddingResult(
            text=text,
            embedding=embedding,
            model=self.model,
            dimensions=len(embedding)
        )

    def embed_batch(
        self,
        texts: List[str],
        input_type: str = "search_document"
    ) -> List[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type=input_type
        )

        return [
            EmbeddingResult(
                text=text,
                embedding=np.array(emb),
                model=self.model,
                dimensions=len(emb)
            )
            for text, emb in zip(texts, response.embeddings)
        ]


class EmbeddingSimilarity:
    """Calculate similarity between embeddings."""

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity.

        Args:
            emb1: First embedding
            emb2: Second embedding

        Returns:
            Similarity score (0 to 1)
        """
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def euclidean_distance(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate Euclidean distance."""
        return np.linalg.norm(emb1 - emb2)

    @staticmethod
    def manhattan_distance(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate Manhattan distance."""
        return np.sum(np.abs(emb1 - emb2))

    @staticmethod
    def find_most_similar(
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar embeddings.

        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of results to return

        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = [
            EmbeddingSimilarity.cosine_similarity(query_embedding, emb)
            for emb in candidate_embeddings
        ]

        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [(int(idx), similarities[idx]) for idx in top_indices]


class SemanticSearch:
    """Semantic search using embeddings."""

    def __init__(self, embedder):
        """
        Initialize semantic search.

        Args:
            embedder: Embedding generator (OpenAI, Local, or Cohere)
        """
        self.embedder = embedder
        self.documents: List[str] = []
        self.embeddings: List[np.ndarray] = []

    def add_documents(self, documents: List[str]):
        """
        Add documents to search index.

        Args:
            documents: List of documents
        """
        self.documents.extend(documents)

        # Generate embeddings
        results = self.embedder.embed_batch(documents)
        self.embeddings.extend([r.embedding for r in results])

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of (document, score) tuples
        """
        if not self.documents:
            return []

        # Generate query embedding
        query_result = self.embedder.embed(query)
        query_embedding = query_result.embedding

        # Find most similar
        results = EmbeddingSimilarity.find_most_similar(
            query_embedding,
            self.embeddings,
            top_k=top_k
        )

        return [
            (self.documents[idx], score)
            for idx, score in results
        ]

    def clear(self):
        """Clear all documents and embeddings."""
        self.documents = []
        self.embeddings = []


class EmbeddingCache:
    """Cache embeddings to avoid recomputation."""

    def __init__(self, embedder):
        """Initialize cache."""
        self.embedder = embedder
        self.cache: Dict[str, np.ndarray] = {}

    def embed(self, text: str) -> EmbeddingResult:
        """Get embedding with caching."""
        if text in self.cache:
            return EmbeddingResult(
                text=text,
                embedding=self.cache[text],
                model=self.embedder.model_name if hasattr(self.embedder, 'model_name') else "cached",
                dimensions=len(self.cache[text])
            )

        result = self.embedder.embed(text)
        self.cache[text] = result.embedding

        return result

    def clear_cache(self):
        """Clear the cache."""
        self.cache = {}

    def get_cache_size(self) -> int:
        """Get number of cached embeddings."""
        return len(self.cache)


# Usage Examples
if __name__ == "__main__":
    # Example 1: Local embeddings
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        print("=== Local Embeddings ===")
        local_embedder = LocalEmbeddings("all-MiniLM-L6-v2")

        result = local_embedder.embed("Hello, world!")
        print(f"Text: {result.text}")
        print(f"Model: {result.model}")
        print(f"Dimensions: {result.dimensions}")
        print(f"Embedding (first 5): {result.embedding[:5]}\n")

        # Batch embedding
        texts = ["Python is great", "I love programming", "Machine learning is fun"]
        batch_results = local_embedder.embed_batch(texts)
        print(f"Batch embedded {len(batch_results)} texts\n")

    # Example 2: Similarity
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        print("=== Similarity Calculation ===")
        text1 = "I love machine learning"
        text2 = "AI and ML are exciting"
        text3 = "I enjoy cooking pasta"

        emb1 = local_embedder.embed(text1).embedding
        emb2 = local_embedder.embed(text2).embedding
        emb3 = local_embedder.embed(text3).embedding

        sim_calc = EmbeddingSimilarity()

        sim_12 = sim_calc.cosine_similarity(emb1, emb2)
        sim_13 = sim_calc.cosine_similarity(emb1, emb3)

        print(f"Similarity (text1, text2): {sim_12:.4f}")
        print(f"Similarity (text1, text3): {sim_13:.4f}\n")

    # Example 3: Semantic search
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        print("=== Semantic Search ===")
        search = SemanticSearch(local_embedder)

        documents = [
            "Python is a high-level programming language",
            "Machine learning is a subset of artificial intelligence",
            "Deep learning uses neural networks",
            "JavaScript is used for web development",
            "Data science involves analyzing data"
        ]

        search.add_documents(documents)

        results = search.search("What is AI?", top_k=3)

        print("Query: What is AI?")
        print("Top results:")
        for doc, score in results:
            print(f"  - {doc} (score: {score:.4f})")
