"""
Token Optimization Utilities
Tools for optimizing token usage and reducing API costs.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import tiktoken
import re


@dataclass
class TokenStats:
    """Container for token statistics."""
    text: str
    token_count: int
    char_count: int
    tokens_per_char: float
    estimated_cost: float


class TokenCounter:
    """Count tokens for various models."""

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize token counter.

        Args:
            model: Model name for encoding
        """
        self.model = model
        self.encoding = self._get_encoding(model)

    def _get_encoding(self, model: str):
        """Get appropriate encoding for model."""
        try:
            return tiktoken.encoding_for_model(model)
        except KeyError:
            # Default to cl100k_base for unknown models
            return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Token count
        """
        return len(self.encoding.encode(text))

    def count_message_tokens(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4"
    ) -> int:
        """
        Count tokens in message list (chat format).

        Args:
            messages: List of message dictionaries
            model: Model name

        Returns:
            Total token count including formatting
        """
        tokens_per_message = 3  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = 1  # If there's a name, the role is omitted

        num_tokens = 0

        for message in messages:
            num_tokens += tokens_per_message

            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))

                if key == "name":
                    num_tokens += tokens_per_name

        num_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>

        return num_tokens

    def get_stats(
        self,
        text: str,
        cost_per_1k_tokens: float = 0.03
    ) -> TokenStats:
        """
        Get comprehensive token statistics.

        Args:
            text: Input text
            cost_per_1k_tokens: Cost per 1000 tokens

        Returns:
            TokenStats object
        """
        token_count = self.count_tokens(text)
        char_count = len(text)
        tokens_per_char = token_count / char_count if char_count > 0 else 0
        estimated_cost = (token_count / 1000) * cost_per_1k_tokens

        return TokenStats(
            text=text,
            token_count=token_count,
            char_count=char_count,
            tokens_per_char=tokens_per_char,
            estimated_cost=estimated_cost
        )


class TokenOptimizer:
    """Optimize text to reduce token count."""

    def __init__(self, counter: TokenCounter):
        """
        Initialize optimizer.

        Args:
            counter: TokenCounter instance
        """
        self.counter = counter

    def remove_whitespace(self, text: str) -> str:
        """
        Remove unnecessary whitespace.

        Args:
            text: Input text

        Returns:
            Optimized text
        """
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]

        # Remove empty lines
        lines = [line for line in lines if line]

        # Join with single newline
        return '\n'.join(lines)

    def compress_json(self, json_str: str) -> str:
        """
        Compress JSON by removing whitespace.

        Args:
            json_str: JSON string

        Returns:
            Compressed JSON
        """
        import json

        try:
            obj = json.loads(json_str)
            return json.dumps(obj, separators=(',', ':'))
        except json.JSONDecodeError:
            return json_str

    def abbreviate_common_phrases(self, text: str) -> str:
        """
        Replace common phrases with abbreviations.

        Args:
            text: Input text

        Returns:
            Abbreviated text
        """
        abbreviations = {
            "for example": "e.g.",
            "that is": "i.e.",
            "and so on": "etc.",
            "as soon as possible": "ASAP",
            "frequently asked questions": "FAQ"
        }

        result = text

        for phrase, abbrev in abbreviations.items():
            result = result.replace(phrase, abbrev)
            result = result.replace(phrase.title(), abbrev)

        return result

    def truncate_to_token_limit(
        self,
        text: str,
        max_tokens: int,
        truncate_from: str = "end"
    ) -> str:
        """
        Truncate text to fit token limit.

        Args:
            text: Input text
            max_tokens: Maximum tokens allowed
            truncate_from: "start" or "end"

        Returns:
            Truncated text
        """
        tokens = self.counter.encoding.encode(text)

        if len(tokens) <= max_tokens:
            return text

        if truncate_from == "end":
            truncated_tokens = tokens[:max_tokens]
        else:  # start
            truncated_tokens = tokens[-max_tokens:]

        return self.counter.encoding.decode(truncated_tokens)

    def chunk_by_tokens(
        self,
        text: str,
        chunk_size: int,
        overlap: int = 0
    ) -> List[str]:
        """
        Split text into chunks by token count.

        Args:
            text: Input text
            chunk_size: Maximum tokens per chunk
            overlap: Number of overlapping tokens

        Returns:
            List of text chunks
        """
        tokens = self.counter.encoding.encode(text)
        chunks = []

        start = 0

        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]

            chunk_text = self.counter.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            start = end - overlap

        return chunks

    def optimize_prompt(self, prompt: str) -> Tuple[str, int, int]:
        """
        Apply multiple optimization techniques.

        Args:
            prompt: Input prompt

        Returns:
            Tuple of (optimized_prompt, original_tokens, new_tokens)
        """
        original_tokens = self.counter.count_tokens(prompt)

        # Apply optimizations
        optimized = prompt
        optimized = self.remove_whitespace(optimized)
        optimized = self.abbreviate_common_phrases(optimized)

        new_tokens = self.counter.count_tokens(optimized)

        return optimized, original_tokens, new_tokens


class ContextWindowManager:
    """Manage context window for long conversations."""

    def __init__(
        self,
        counter: TokenCounter,
        max_tokens: int = 8000,
        reserve_for_response: int = 1000
    ):
        """
        Initialize context window manager.

        Args:
            counter: TokenCounter instance
            max_tokens: Maximum context window size
            reserve_for_response: Tokens to reserve for response
        """
        self.counter = counter
        self.max_tokens = max_tokens
        self.reserve_for_response = reserve_for_response
        self.available_tokens = max_tokens - reserve_for_response

    def fit_messages(
        self,
        messages: List[Dict[str, str]],
        system_message: Optional[str] = None,
        keep_recent: int = 5
    ) -> List[Dict[str, str]]:
        """
        Fit messages within context window.

        Args:
            messages: List of messages
            system_message: Optional system message (always kept)
            keep_recent: Number of recent messages to always keep

        Returns:
            Fitted messages list
        """
        result = []

        # Always include system message
        if system_message:
            result.append({"role": "system", "content": system_message})

        # Ensure we keep most recent messages
        if len(messages) <= keep_recent:
            return result + messages

        # Calculate tokens
        current_tokens = self.counter.count_message_tokens(result)

        # Add recent messages (from end)
        recent_messages = messages[-keep_recent:]
        recent_tokens = self.counter.count_message_tokens(recent_messages)

        current_tokens += recent_tokens

        # Add older messages if space available
        older_messages = messages[:-keep_recent]

        for msg in reversed(older_messages):
            msg_tokens = self.counter.count_message_tokens([msg])

            if current_tokens + msg_tokens <= self.available_tokens:
                result.insert(1 if system_message else 0, msg)
                current_tokens += msg_tokens
            else:
                break

        # Add recent messages
        result.extend(recent_messages)

        return result

    def summarize_old_messages(
        self,
        messages: List[Dict[str, str]],
        summary_prompt: str = "Summarize the following conversation concisely:"
    ) -> str:
        """
        Create summary of old messages.

        Args:
            messages: Messages to summarize
            summary_prompt: Prompt for summarization

        Returns:
            Summary text
        """
        conversation = "\n\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        )

        return f"{summary_prompt}\n\n{conversation}"


# Usage Examples
if __name__ == "__main__":
    # Initialize counter
    counter = TokenCounter(model="gpt-4")

    # Count tokens
    text = "This is a sample text for token counting."
    token_count = counter.count_tokens(text)
    print(f"Text: {text}")
    print(f"Tokens: {token_count}\n")

    # Get statistics
    stats = counter.get_stats(
        text="Hello, how are you doing today? I hope you're having a great day!",
        cost_per_1k_tokens=0.03
    )

    print(f"Token Stats:")
    print(f"  Tokens: {stats.token_count}")
    print(f"  Characters: {stats.char_count}")
    print(f"  Tokens/Char: {stats.tokens_per_char:.3f}")
    print(f"  Estimated Cost: ${stats.estimated_cost:.6f}\n")

    # Count message tokens
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."}
    ]

    message_tokens = counter.count_message_tokens(messages)
    print(f"Message tokens: {message_tokens}\n")

    # Optimize prompt
    optimizer = TokenOptimizer(counter)

    long_prompt = """
    Please   help   me   with   the   following   task.


    For example, I would like to know how to do this.

    That is very important for my work.
    """

    optimized, original, new = optimizer.optimize_prompt(long_prompt)

    print(f"Original tokens: {original}")
    print(f"Optimized tokens: {new}")
    print(f"Saved: {original - new} tokens ({((original - new) / original * 100):.1f}%)\n")
    print(f"Optimized text:\n{optimized}\n")

    # Truncate text
    long_text = "This is a very long text. " * 100
    truncated = optimizer.truncate_to_token_limit(long_text, max_tokens=50)

    print(f"Original length: {counter.count_tokens(long_text)} tokens")
    print(f"Truncated length: {counter.count_tokens(truncated)} tokens")
    print(f"Truncated text: {truncated[:100]}...\n")

    # Chunk by tokens
    chunks = optimizer.chunk_by_tokens(long_text, chunk_size=50, overlap=10)
    print(f"Number of chunks: {len(chunks)}")
    print(f"First chunk tokens: {counter.count_tokens(chunks[0])}")

    # Context window management
    context_manager = ContextWindowManager(
        counter,
        max_tokens=4000,
        reserve_for_response=500
    )

    many_messages = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(100)
    ]

    fitted = context_manager.fit_messages(
        many_messages,
        system_message="You are helpful.",
        keep_recent=5
    )

    print(f"\nOriginal messages: {len(many_messages)}")
    print(f"Fitted messages: {len(fitted)}")
    print(f"Total tokens: {counter.count_message_tokens(fitted)}")
