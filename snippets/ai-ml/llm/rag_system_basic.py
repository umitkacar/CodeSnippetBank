"""
RAG (Retrieval-Augmented Generation) System
Production-ready RAG implementation with vector database and LLM.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class Document:
    """Container for document with metadata."""
    content: str
    metadata: Dict[str, Any]
    doc_id: Optional[str] = None


@dataclass
class RetrievalResult:
    """Container for retrieval results."""
    documents: List[Document]
    scores: List[float]
    query: str


@dataclass
class RAGResponse:
    """Container for RAG system response."""
    answer: str
    sources: List[Document]
    retrieval_scores: List[float]
    context_used: str


class VectorStore:
    """Vector database for document storage and retrieval."""

    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
            embedding_model: Sentence transformer model name

        Raises:
            ImportError: If required packages not installed
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed")

        self.embedding_model = SentenceTransformer(embedding_model)

        # Initialize ChromaDB
        if persist_directory:
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store.

        Args:
            documents: List of Document objects
        """
        if not documents:
            return

        # Generate embeddings
        texts = [doc.content for doc in documents]
        embeddings = self.embedding_model.encode(texts).tolist()

        # Prepare data for ChromaDB
        ids = [
            doc.doc_id or f"doc_{i}"
            for i, doc in enumerate(documents)
        ]
        metadatas = [doc.metadata for doc in documents]

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> RetrievalResult:
        """
        Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            RetrievalResult object
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()

        # Search
        where_filter = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        # Parse results
        documents = []
        scores = []

        if results["documents"] and results["documents"][0]:
            for i, (doc_text, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                documents.append(Document(
                    content=doc_text,
                    metadata=metadata,
                    doc_id=results["ids"][0][i]
                ))
                # Convert distance to similarity score (1 - cosine distance)
                scores.append(1 - distance)

        return RetrievalResult(
            documents=documents,
            scores=scores,
            query=query
        )

    def delete_collection(self) -> None:
        """Delete the collection."""
        self.client.delete_collection(self.collection.name)


class RAGSystem:
    """Complete RAG system with retrieval and generation."""

    def __init__(
        self,
        vector_store: VectorStore,
        llm_model: str = "gpt-4-turbo-preview",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize RAG system.

        Args:
            vector_store: VectorStore instance
            llm_model: LLM model name
            api_key: OpenAI API key
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Raises:
            ImportError: If OpenAI not installed
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")

        self.vector_store = vector_store
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def query(
        self,
        question: str,
        top_k: int = 3,
        system_prompt: Optional[str] = None,
        include_sources: bool = True
    ) -> RAGResponse:
        """
        Query the RAG system.

        Args:
            question: User question
            top_k: Number of documents to retrieve
            system_prompt: Optional system prompt
            include_sources: Whether to include source info

        Returns:
            RAGResponse object
        """
        # Retrieve relevant documents
        retrieval_result = self.vector_store.search(question, top_k=top_k)

        if not retrieval_result.documents:
            return RAGResponse(
                answer="No relevant information found.",
                sources=[],
                retrieval_scores=[],
                context_used=""
            )

        # Build context from retrieved documents
        context = self._build_context(retrieval_result.documents)

        # Generate response
        answer = self._generate_response(
            question=question,
            context=context,
            system_prompt=system_prompt
        )

        return RAGResponse(
            answer=answer,
            sources=retrieval_result.documents,
            retrieval_scores=retrieval_result.scores,
            context_used=context
        )

    def _build_context(self, documents: List[Document]) -> str:
        """Build context string from documents."""
        context_parts = []

        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Document {i}]")
            context_parts.append(doc.content)
            context_parts.append("")

        return "\n".join(context_parts)

    def _generate_response(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using LLM."""
        default_system = """You are a helpful assistant that answers questions based on the provided context.
If the context doesn't contain enough information to answer the question, say so.
Always cite which document(s) you used to form your answer."""

        system_msg = system_prompt or default_system

        user_prompt = f"""Context:
{context}

Question: {question}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Generation error: {e}")
            return "Error generating response."

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the system."""
        self.vector_store.add_documents(documents)


class DocumentProcessor:
    """Process documents for RAG system."""

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 512,
        overlap: int = 128
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    @staticmethod
    def load_text_file(file_path: str) -> Document:
        """Load text file as document."""
        path = Path(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return Document(
            content=content,
            metadata={
                "source": str(path),
                "filename": path.name
            }
        )


# Usage Example
if __name__ == "__main__":
    if not (SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE and OPENAI_AVAILABLE):
        print("Required packages not installed. Install with:")
        print("pip install sentence-transformers chromadb openai")
        exit(1)

    # Initialize vector store
    vector_store = VectorStore(
        collection_name="my_documents",
        embedding_model="all-MiniLM-L6-v2"
    )

    # Prepare sample documents
    documents = [
        Document(
            content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including object-oriented, functional, and procedural programming.",
            metadata={"category": "programming", "language": "Python"}
        ),
        Document(
            content="Machine learning is a subset of artificial intelligence that focuses on building systems that can learn from data. Popular frameworks include TensorFlow, PyTorch, and scikit-learn.",
            metadata={"category": "AI", "topic": "machine learning"}
        ),
        Document(
            content="FastAPI is a modern, fast web framework for building APIs with Python. It's based on standard Python type hints and provides automatic API documentation.",
            metadata={"category": "programming", "framework": "FastAPI"}
        )
    ]

    # Add documents to vector store
    vector_store.add_documents(documents)

    # Initialize RAG system
    rag = RAGSystem(vector_store=vector_store)

    # Query the system
    response = rag.query(
        question="What is Python and what are its characteristics?",
        top_k=2
    )

    print(f"Question: What is Python and what are its characteristics?\n")
    print(f"Answer: {response.answer}\n")
    print(f"Sources used: {len(response.sources)}")
    for i, (source, score) in enumerate(zip(response.sources, response.retrieval_scores), 1):
        print(f"\nSource {i} (score: {score:.3f}):")
        print(f"{source.content[:100]}...")
