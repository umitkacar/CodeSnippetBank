"""
Conversation Memory Management
Manage conversation history with various memory strategies.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from collections import deque


@dataclass
class Message:
    """Container for a single message."""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationSummary:
    """Container for conversation summary."""
    summary: str
    message_count: int
    created_at: datetime = field(default_factory=datetime.now)


class BufferMemory:
    """Simple buffer-based memory (keep last K messages)."""

    def __init__(self, max_messages: int = 10):
        """
        Initialize buffer memory.

        Args:
            max_messages: Maximum messages to keep
        """
        self.max_messages = max_messages
        self.messages: deque = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to memory."""
        self.messages.append(Message(role, content, metadata=metadata))

    def get_messages(self) -> List[Message]:
        """Get all messages in memory."""
        return list(self.messages)

    def get_formatted_messages(self) -> List[Dict[str, str]]:
        """Get messages in API format."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]

    def clear(self):
        """Clear all messages."""
        self.messages.clear()


class SummaryMemory:
    """Memory with automatic summarization of old messages."""

    def __init__(
        self,
        max_messages: int = 10,
        summarize_threshold: int = 8
    ):
        """
        Initialize summary memory.

        Args:
            max_messages: Maximum messages before summarization
            summarize_threshold: Trigger summarization at this count
        """
        self.max_messages = max_messages
        self.summarize_threshold = summarize_threshold
        self.messages: List[Message] = []
        self.summaries: List[ConversationSummary] = []

    def add_message(self, role: str, content: str):
        """Add message and trigger summarization if needed."""
        self.messages.append(Message(role, content))

        if len(self.messages) >= self.summarize_threshold:
            self._summarize_old_messages()

    def _summarize_old_messages(self):
        """Summarize old messages (placeholder - use LLM in production)."""
        # In production, use LLM to create summary
        messages_to_summarize = self.messages[:-self.max_messages]

        if not messages_to_summarize:
            return

        summary_text = f"Conversation covered {len(messages_to_summarize)} messages about various topics."

        self.summaries.append(ConversationSummary(
            summary=summary_text,
            message_count=len(messages_to_summarize)
        ))

        # Keep only recent messages
        self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> str:
        """Get full context including summaries."""
        parts = []

        # Add summaries
        if self.summaries:
            parts.append("Previous conversation summary:")
            for summary in self.summaries:
                parts.append(summary.summary)
            parts.append("")

        # Add recent messages
        parts.append("Recent messages:")
        for msg in self.messages:
            parts.append(f"{msg.role}: {msg.content}")

        return "\n".join(parts)

    def get_formatted_messages(self) -> List[Dict[str, str]]:
        """Get messages in API format."""
        messages = []

        # Add summary as system message if available
        if self.summaries:
            summary_text = " ".join(s.summary for s in self.summaries)
            messages.append({
                "role": "system",
                "content": f"Previous conversation context: {summary_text}"
            })

        # Add recent messages
        messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ])

        return messages


class EntityMemory:
    """Memory that tracks entities mentioned in conversation."""

    def __init__(self):
        """Initialize entity memory."""
        self.entities: Dict[str, List[str]] = {}
        self.messages: List[Message] = []

    def add_message(self, role: str, content: str):
        """Add message and extract entities."""
        self.messages.append(Message(role, content))
        self._extract_entities(content)

    def _extract_entities(self, text: str):
        """Extract entities from text (simple implementation)."""
        # In production, use NER model
        words = text.split()

        for word in words:
            # Simple heuristic: capitalized words as entities
            if word[0].isupper() and len(word) > 1:
                entity_type = "PERSON"  # Simplified

                if entity_type not in self.entities:
                    self.entities[entity_type] = []

                if word not in self.entities[entity_type]:
                    self.entities[entity_type].append(word)

    def get_entities(self) -> Dict[str, List[str]]:
        """Get all tracked entities."""
        return self.entities.copy()

    def get_entity_context(self) -> str:
        """Get formatted entity information."""
        if not self.entities:
            return ""

        parts = ["Known entities:"]

        for entity_type, entities in self.entities.items():
            parts.append(f"  {entity_type}: {', '.join(entities)}")

        return "\n".join(parts)


class VectorMemory:
    """Memory using vector similarity for relevant context retrieval."""

    def __init__(self, embedding_function):
        """
        Initialize vector memory.

        Args:
            embedding_function: Function to generate embeddings
        """
        self.embedding_function = embedding_function
        self.messages: List[Message] = []
        self.embeddings: List[Any] = []

    def add_message(self, role: str, content: str):
        """Add message with embedding."""
        message = Message(role, content)
        self.messages.append(message)

        # Generate embedding
        embedding = self.embedding_function(content)
        self.embeddings.append(embedding)

    def get_relevant_messages(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Message]:
        """
        Get most relevant messages for query.

        Args:
            query: Query text
            top_k: Number of messages to retrieve

        Returns:
            List of relevant messages
        """
        if not self.messages:
            return []

        # Generate query embedding
        query_embedding = self.embedding_function(query)

        # Calculate similarities (cosine similarity)
        import numpy as np

        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [self.messages[i] for i in top_indices]


class ConversationMemoryManager:
    """Manage multiple memory types together."""

    def __init__(
        self,
        buffer_size: int = 10,
        use_summary: bool = True,
        use_entities: bool = True
    ):
        """
        Initialize memory manager.

        Args:
            buffer_size: Size of buffer memory
            use_summary: Enable summary memory
            use_entities: Enable entity tracking
        """
        self.buffer = BufferMemory(max_messages=buffer_size)
        self.summary = SummaryMemory() if use_summary else None
        self.entities = EntityMemory() if use_entities else None

    def add_message(self, role: str, content: str):
        """Add message to all memory types."""
        self.buffer.add_message(role, content)

        if self.summary:
            self.summary.add_message(role, content)

        if self.entities:
            self.entities.add_message(role, content)

    def get_context_for_llm(self, include_entities: bool = True) -> List[Dict[str, str]]:
        """
        Get formatted context for LLM.

        Args:
            include_entities: Whether to include entity information

        Returns:
            List of messages for LLM
        """
        messages = []

        # Add entity context as system message
        if include_entities and self.entities:
            entity_context = self.entities.get_entity_context()
            if entity_context:
                messages.append({
                    "role": "system",
                    "content": entity_context
                })

        # Add conversation history
        if self.summary:
            messages.extend(self.summary.get_formatted_messages())
        else:
            messages.extend(self.buffer.get_formatted_messages())

        return messages

    def save(self, filepath: str):
        """Save memory to file."""
        data = {
            "buffer": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.buffer.get_messages()
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """Load memory from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.buffer.clear()

        for msg_data in data.get("buffer", []):
            self.buffer.add_message(
                msg_data["role"],
                msg_data["content"]
            )


# Usage Examples
if __name__ == "__main__":
    # Example 1: Buffer Memory
    print("=== Buffer Memory ===")
    buffer = BufferMemory(max_messages=5)

    buffer.add_message("user", "Hello!")
    buffer.add_message("assistant", "Hi! How can I help?")
    buffer.add_message("user", "What's the weather?")
    buffer.add_message("assistant", "I don't have weather data.")
    buffer.add_message("user", "Tell me a joke.")
    buffer.add_message("assistant", "Why did the chicken cross the road?")
    buffer.add_message("user", "Why?")  # This will push out the first message

    messages = buffer.get_formatted_messages()
    print(f"Buffer contains {len(messages)} messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    print()

    # Example 2: Summary Memory
    print("=== Summary Memory ===")
    summary = SummaryMemory(max_messages=3, summarize_threshold=5)

    for i in range(10):
        summary.add_message("user", f"Message {i}")
        summary.add_message("assistant", f"Response {i}")

    print(f"Summaries created: {len(summary.summaries)}")
    print(f"Recent messages: {len(summary.messages)}")
    print()

    # Example 3: Entity Memory
    print("=== Entity Memory ===")
    entity_mem = EntityMemory()

    entity_mem.add_message("user", "My name is John and I live in Paris")
    entity_mem.add_message("assistant", "Nice to meet you John!")
    entity_mem.add_message("user", "I work with Sarah and Mike")

    entities = entity_mem.get_entities()
    print("Extracted entities:")
    print(entities)
    print()

    # Example 4: Memory Manager
    print("=== Memory Manager ===")
    manager = ConversationMemoryManager(
        buffer_size=5,
        use_summary=True,
        use_entities=True
    )

    manager.add_message("user", "Hello, my name is Alice")
    manager.add_message("assistant", "Hi Alice! Nice to meet you.")
    manager.add_message("user", "I'm interested in Python")
    manager.add_message("assistant", "Python is a great language!")

    context = manager.get_context_for_llm()
    print(f"Context messages: {len(context)}")
    for msg in context:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    print()

    # Save and load
    manager.save("/tmp/conversation_memory.json")
    print("Memory saved to /tmp/conversation_memory.json")

    new_manager = ConversationMemoryManager()
    new_manager.load("/tmp/conversation_memory.json")
    print(f"Loaded {len(new_manager.buffer.get_messages())} messages")
