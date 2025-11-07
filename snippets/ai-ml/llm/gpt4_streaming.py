"""
GPT-4 Streaming Responses
Real-time token streaming for better UX and lower latency perception.
"""

import os
from typing import Iterator, Optional, Callable
from dataclasses import dataclass
from openai import OpenAI
import sys


@dataclass
class StreamChunk:
    """Container for streaming response chunks."""
    content: str
    finish_reason: Optional[str] = None
    model: Optional[str] = None


class GPT4Streamer:
    """Stream GPT-4 responses token-by-token."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize streaming client.

        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def stream_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Iterator[StreamChunk]:
        """
        Stream completion tokens as they're generated.

        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Yields:
            StreamChunk objects containing token content

        Raises:
            openai.OpenAIError: On API errors
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        finish_reason=chunk.choices[0].finish_reason,
                        model=chunk.model
                    )

        except Exception as e:
            print(f"Streaming error: {e}")
            raise

    def stream_with_callback(
        self,
        prompt: str,
        callback: Callable[[str], None],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Stream completion with callback for each token.

        Args:
            prompt: User prompt
            callback: Function called with each token
            system_message: Optional system message
            **kwargs: Additional parameters

        Returns:
            Complete response text
        """
        full_response = []

        for chunk in self.stream_completion(prompt, system_message, **kwargs):
            callback(chunk.content)
            full_response.append(chunk.content)

        return "".join(full_response)

    def stream_to_stdout(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Stream completion directly to stdout.

        Args:
            prompt: User prompt
            system_message: Optional system message
            **kwargs: Additional parameters

        Returns:
            Complete response text
        """
        def print_token(token: str):
            sys.stdout.write(token)
            sys.stdout.flush()

        response = self.stream_with_callback(
            prompt,
            print_token,
            system_message,
            **kwargs
        )

        print()  # New line after completion
        return response

    def stream_with_buffer(
        self,
        prompt: str,
        buffer_size: int = 5,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream with buffering for smoother output.

        Args:
            prompt: User prompt
            buffer_size: Number of tokens to buffer
            system_message: Optional system message
            **kwargs: Additional parameters

        Yields:
            Buffered chunks of text
        """
        buffer = []

        for chunk in self.stream_completion(prompt, system_message, **kwargs):
            buffer.append(chunk.content)

            if len(buffer) >= buffer_size:
                yield "".join(buffer)
                buffer = []

        # Yield remaining buffer
        if buffer:
            yield "".join(buffer)


class StreamingChatSession:
    """Maintain a streaming chat session with history."""

    def __init__(self, streamer: GPT4Streamer, system_message: Optional[str] = None):
        """
        Initialize chat session.

        Args:
            streamer: GPT4Streamer instance
            system_message: Optional system message
        """
        self.streamer = streamer
        self.messages = []

        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def chat_stream(self, user_message: str) -> Iterator[StreamChunk]:
        """
        Add user message and stream assistant response.

        Args:
            user_message: User's message

        Yields:
            StreamChunk objects
        """
        self.messages.append({"role": "user", "content": user_message})

        try:
            stream = self.streamer.client.chat.completions.create(
                model=self.streamer.model,
                messages=self.messages,
                stream=True
            )

            assistant_message = []

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_message.append(content)

                    yield StreamChunk(
                        content=content,
                        finish_reason=chunk.choices[0].finish_reason
                    )

            # Add complete assistant message to history
            self.messages.append({
                "role": "assistant",
                "content": "".join(assistant_message)
            })

        except Exception as e:
            print(f"Chat streaming error: {e}")
            raise


# Usage Examples
if __name__ == "__main__":
    streamer = GPT4Streamer()

    print("=== Example 1: Basic Streaming ===")
    for chunk in streamer.stream_completion("Explain machine learning in 3 sentences."):
        print(chunk.content, end="", flush=True)
    print("\n")

    print("=== Example 2: Stream to stdout ===")
    response = streamer.stream_to_stdout(
        "Write a haiku about coding.",
        system_message="You are a creative poet."
    )
    print(f"Complete response: {len(response)} chars\n")

    print("=== Example 3: Buffered Streaming ===")
    for buffered_chunk in streamer.stream_with_buffer(
        "Count from 1 to 10.",
        buffer_size=3
    ):
        print(f"[Buffer: {buffered_chunk}]", end=" ", flush=True)
    print("\n")

    print("=== Example 4: Chat Session ===")
    session = StreamingChatSession(
        streamer,
        system_message="You are a helpful coding assistant."
    )

    for chunk in session.chat_stream("What is Python?"):
        print(chunk.content, end="", flush=True)
    print("\n")

    for chunk in session.chat_stream("Give me an example."):
        print(chunk.content, end="", flush=True)
    print()
