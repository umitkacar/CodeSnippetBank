"""
GPT-4 Basic Integration with OpenAI API
Production-ready implementation with error handling and retry logic.
"""

import os
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class GPT4Response:
    """Response container for GPT-4 completions."""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    response_time: float


class GPT4Client:
    """Production-ready GPT-4 client with retry logic and error handling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize GPT-4 client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name to use
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> GPT4Response:
        """
        Generate completion with GPT-4.

        Args:
            prompt: User prompt
            system_message: Optional system message
            **kwargs: Additional parameters to override defaults

        Returns:
            GPT4Response object with completion data

        Raises:
            openai.OpenAIError: On API errors after retries
        """
        start_time = time.time()

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0)
            )

            response_time = time.time() - start_time

            return GPT4Response(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time
            )

        except openai.RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            raise
        except openai.APIError as e:
            print(f"API error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def batch_complete(
        self,
        prompts: List[str],
        system_message: Optional[str] = None,
        delay: float = 0.5
    ) -> List[GPT4Response]:
        """
        Process multiple prompts with rate limiting.

        Args:
            prompts: List of prompts to process
            system_message: Optional system message for all prompts
            delay: Delay between requests in seconds

        Returns:
            List of GPT4Response objects
        """
        responses = []

        for i, prompt in enumerate(prompts):
            try:
                response = self.complete(prompt, system_message)
                responses.append(response)

                # Rate limiting
                if i < len(prompts) - 1:
                    time.sleep(delay)

            except Exception as e:
                print(f"Error processing prompt {i}: {e}")
                responses.append(None)

        return responses


# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = GPT4Client(
        model="gpt-4-turbo-preview",
        temperature=0.7
    )

    # Single completion
    response = client.complete(
        prompt="Explain quantum computing in simple terms.",
        system_message="You are a helpful science educator."
    )

    print(f"Response: {response.content}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Response time: {response.response_time:.2f}s")

    # Batch processing
    prompts = [
        "What is machine learning?",
        "Explain neural networks.",
        "What is deep learning?"
    ]

    responses = client.batch_complete(prompts)
    for i, resp in enumerate(responses):
        if resp:
            print(f"\nPrompt {i+1}: {resp.content[:100]}...")
