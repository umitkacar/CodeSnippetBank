"""
Google Gemini API Integration
Production-ready Gemini Pro client with multimodal support.
"""

import os
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image


@dataclass
class GeminiResponse:
    """Response container for Gemini completions."""
    content: str
    model: str
    finish_reason: str
    safety_ratings: List[Dict]
    response_time: float
    token_count: Optional[int] = None


class GeminiClient:
    """Production-ready Google Gemini client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Model name (gemini-pro, gemini-pro-vision)
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided")

        genai.configure(api_key=self.api_key)

        self.model_name = model
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k

        # Configure safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

    def complete(
        self,
        prompt: str,
        **kwargs
    ) -> GeminiResponse:
        """
        Generate completion with Gemini.

        Args:
            prompt: User prompt
            **kwargs: Additional generation parameters

        Returns:
            GeminiResponse object

        Raises:
            Exception: On API errors
        """
        start_time = time.time()

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                top_k=kwargs.get("top_k", self.top_k),
                max_output_tokens=kwargs.get("max_output_tokens", 2048)
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )

            response_time = time.time() - start_time

            # Extract safety ratings
            safety_ratings = [
                {
                    "category": rating.category.name,
                    "probability": rating.probability.name
                }
                for rating in response.candidates[0].safety_ratings
            ]

            return GeminiResponse(
                content=response.text,
                model=self.model_name,
                finish_reason=response.candidates[0].finish_reason.name,
                safety_ratings=safety_ratings,
                response_time=response_time,
                token_count=self.count_tokens(prompt)
            )

        except Exception as e:
            print(f"Gemini API error: {e}")
            raise

    def complete_with_image(
        self,
        prompt: str,
        image_path: str,
        **kwargs
    ) -> GeminiResponse:
        """
        Generate completion with image input (vision model).

        Args:
            prompt: Text prompt
            image_path: Path to image file
            **kwargs: Additional parameters

        Returns:
            GeminiResponse object
        """
        if "vision" not in self.model_name:
            vision_model = genai.GenerativeModel("gemini-pro-vision")
        else:
            vision_model = self.model

        start_time = time.time()

        try:
            image = Image.open(image_path)

            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_output_tokens", 2048)
            )

            response = vision_model.generate_content(
                [prompt, image],
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )

            response_time = time.time() - start_time

            safety_ratings = [
                {
                    "category": rating.category.name,
                    "probability": rating.probability.name
                }
                for rating in response.candidates[0].safety_ratings
            ]

            return GeminiResponse(
                content=response.text,
                model="gemini-pro-vision",
                finish_reason=response.candidates[0].finish_reason.name,
                safety_ratings=safety_ratings,
                response_time=response_time
            )

        except Exception as e:
            print(f"Vision API error: {e}")
            raise

    def stream_complete(self, prompt: str, **kwargs):
        """
        Stream completion tokens.

        Args:
            prompt: User prompt
            **kwargs: Additional parameters

        Yields:
            Text chunks as they arrive
        """
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                top_k=kwargs.get("top_k", self.top_k),
                max_output_tokens=kwargs.get("max_output_tokens", 2048)
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"Streaming error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Token count
        """
        try:
            return self.model.count_tokens(text).total_tokens
        except Exception as e:
            print(f"Token counting error: {e}")
            return 0

    def batch_complete(
        self,
        prompts: List[str],
        delay: float = 1.0
    ) -> List[GeminiResponse]:
        """
        Process multiple prompts with rate limiting.

        Args:
            prompts: List of prompts
            delay: Delay between requests

        Returns:
            List of GeminiResponse objects
        """
        responses = []

        for i, prompt in enumerate(prompts):
            try:
                response = self.complete(prompt)
                responses.append(response)

                if i < len(prompts) - 1:
                    time.sleep(delay)

            except Exception as e:
                print(f"Error processing prompt {i}: {e}")
                responses.append(None)

        return responses


class GeminiChatSession:
    """Maintain a conversation with Gemini."""

    def __init__(self, client: GeminiClient):
        """
        Initialize chat session.

        Args:
            client: GeminiClient instance
        """
        self.client = client
        self.chat = client.model.start_chat(history=[])

    def send_message(self, message: str) -> GeminiResponse:
        """
        Send a message in the chat.

        Args:
            message: User message

        Returns:
            GeminiResponse object
        """
        start_time = time.time()

        try:
            response = self.chat.send_message(
                message,
                safety_settings=self.client.safety_settings
            )

            response_time = time.time() - start_time

            safety_ratings = [
                {
                    "category": rating.category.name,
                    "probability": rating.probability.name
                }
                for rating in response.candidates[0].safety_ratings
            ]

            return GeminiResponse(
                content=response.text,
                model=self.client.model_name,
                finish_reason=response.candidates[0].finish_reason.name,
                safety_ratings=safety_ratings,
                response_time=response_time
            )

        except Exception as e:
            print(f"Chat error: {e}")
            raise

    def get_history(self) -> List[Dict[str, str]]:
        """Get chat history."""
        return [
            {
                "role": msg.role,
                "content": "".join(part.text for part in msg.parts)
            }
            for msg in self.chat.history
        ]

    def clear_history(self):
        """Clear chat history."""
        self.chat = self.client.model.start_chat(history=[])


# Usage Examples
if __name__ == "__main__":
    # Initialize client
    client = GeminiClient(
        model="gemini-pro",
        temperature=0.7
    )

    # Single completion
    response = client.complete("Explain quantum entanglement in simple terms.")
    print(f"Response: {response.content[:200]}...")
    print(f"Tokens: {response.token_count}")
    print(f"Time: {response.response_time:.2f}s")
    print(f"Safety: {response.safety_ratings}\n")

    # Streaming
    print("Streaming response:")
    for chunk in client.stream_complete("Write a haiku about AI."):
        print(chunk, end="", flush=True)
    print("\n")

    # Chat session
    session = GeminiChatSession(client)

    resp1 = session.send_message("What is machine learning?")
    print(f"Chat 1: {resp1.content[:150]}...\n")

    resp2 = session.send_message("Give me a Python example.")
    print(f"Chat 2: {resp2.content[:150]}...\n")

    # Token counting
    token_count = client.count_tokens("This is a test prompt for token counting.")
    print(f"Token count: {token_count}\n")

    # Batch processing
    prompts = [
        "What is Python?",
        "What is JavaScript?",
        "What is Go?"
    ]

    batch_responses = client.batch_complete(prompts, delay=0.5)
    for i, resp in enumerate(batch_responses):
        if resp:
            print(f"Batch {i+1}: {resp.content[:100]}...")
