"""
LLaMA Local Inference
Run LLaMA models locally using llama-cpp-python and transformers.
"""

import os
from typing import Optional, List, Dict, Any, Iterator
from dataclasses import dataclass
import time
from pathlib import Path


try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class LLaMAResponse:
    """Response container for LLaMA completions."""
    content: str
    model: str
    tokens_generated: int
    response_time: float
    tokens_per_second: float


class LLaMALocalClient:
    """Run LLaMA models locally with llama-cpp-python (GGUF format)."""

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: Optional[int] = None,
        n_gpu_layers: int = 0,
        verbose: bool = False
    ):
        """
        Initialize LLaMA client with GGUF model.

        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_threads: Number of CPU threads
            n_gpu_layers: Number of layers to offload to GPU
            verbose: Enable verbose logging

        Raises:
            ImportError: If llama-cpp-python not installed
            FileNotFoundError: If model file not found
        """
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python not installed. Install with: pip install llama-cpp-python")

        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self.model_path = model_path
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose
        )

    def complete(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        stop: Optional[List[str]] = None
    ) -> LLaMAResponse:
        """
        Generate completion.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Repetition penalty
            stop: Stop sequences

        Returns:
            LLaMAResponse object
        """
        start_time = time.time()

        try:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop=stop or []
            )

            response_time = time.time() - start_time
            tokens_generated = output["usage"]["completion_tokens"]
            tokens_per_second = tokens_generated / response_time if response_time > 0 else 0

            return LLaMAResponse(
                content=output["choices"][0]["text"],
                model=self.model_path,
                tokens_generated=tokens_generated,
                response_time=response_time,
                tokens_per_second=tokens_per_second
            )

        except Exception as e:
            print(f"Completion error: {e}")
            raise

    def stream_complete(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.8,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream completion tokens.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Yields:
            Generated text chunks
        """
        try:
            stream = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            for output in stream:
                yield output["choices"][0]["text"]

        except Exception as e:
            print(f"Streaming error: {e}")
            raise

    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 256,
        temperature: float = 0.8
    ) -> LLaMAResponse:
        """
        Chat completion with conversation format.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLaMAResponse object
        """
        start_time = time.time()

        try:
            output = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            response_time = time.time() - start_time
            tokens_generated = output["usage"]["completion_tokens"]
            tokens_per_second = tokens_generated / response_time if response_time > 0 else 0

            return LLaMAResponse(
                content=output["choices"][0]["message"]["content"],
                model=self.model_path,
                tokens_generated=tokens_generated,
                response_time=response_time,
                tokens_per_second=tokens_per_second
            )

        except Exception as e:
            print(f"Chat completion error: {e}")
            raise


class LLaMATransformersClient:
    """Run LLaMA models with HuggingFace Transformers."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-chat-hf",
        device: str = "auto",
        load_in_8bit: bool = False,
        load_in_4bit: bool = False
    ):
        """
        Initialize LLaMA with Transformers.

        Args:
            model_name: HuggingFace model name
            device: Device to run on ('cuda', 'cpu', 'auto')
            load_in_8bit: Load model in 8-bit precision
            load_in_4bit: Load model in 4-bit precision

        Raises:
            ImportError: If transformers not installed
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers not installed. Install with: pip install transformers torch")

        self.model_name = model_name

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Load model with quantization if requested
        model_kwargs = {"device_map": device}

        if load_in_8bit:
            model_kwargs["load_in_8bit"] = True
        elif load_in_4bit:
            model_kwargs["load_in_4bit"] = True

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs
        )

        # Create pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer
        )

    def complete(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.8,
        top_p: float = 0.95,
        do_sample: bool = True
    ) -> LLaMAResponse:
        """
        Generate completion.

        Args:
            prompt: Input prompt
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            do_sample: Whether to use sampling

        Returns:
            LLaMAResponse object
        """
        start_time = time.time()

        try:
            outputs = self.pipe(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                return_full_text=False
            )

            response_time = time.time() - start_time
            content = outputs[0]["generated_text"]

            # Estimate tokens (rough approximation)
            tokens_generated = len(self.tokenizer.encode(content))
            tokens_per_second = tokens_generated / response_time if response_time > 0 else 0

            return LLaMAResponse(
                content=content,
                model=self.model_name,
                tokens_generated=tokens_generated,
                response_time=response_time,
                tokens_per_second=tokens_per_second
            )

        except Exception as e:
            print(f"Completion error: {e}")
            raise

    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 256,
        temperature: float = 0.8
    ) -> LLaMAResponse:
        """
        Chat completion with conversation format.

        Args:
            messages: List of message dicts
            max_new_tokens: Maximum new tokens
            temperature: Sampling temperature

        Returns:
            LLaMAResponse object
        """
        # Format messages for LLaMA-2 chat format
        prompt = self._format_chat_messages(messages)
        return self.complete(prompt, max_new_tokens, temperature)

    def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages in LLaMA-2 chat format."""
        formatted = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                formatted += f"<<SYS>>\n{content}\n<</SYS>>\n\n"
            elif role == "user":
                formatted += f"[INST] {content} [/INST] "
            elif role == "assistant":
                formatted += f"{content} "

        return formatted


# Usage Examples
if __name__ == "__main__":
    # Example 1: llama-cpp-python (GGUF)
    if LLAMA_CPP_AVAILABLE:
        print("=== LLaMA with llama-cpp-python ===")

        # Initialize with GGUF model
        client = LLaMALocalClient(
            model_path="/path/to/llama-2-7b.gguf",
            n_ctx=2048,
            n_gpu_layers=32  # Offload to GPU
        )

        # Simple completion
        response = client.complete(
            "def fibonacci(n):",
            max_tokens=128,
            temperature=0.7
        )

        print(f"Response: {response.content}")
        print(f"Tokens/sec: {response.tokens_per_second:.2f}")
        print(f"Time: {response.response_time:.2f}s\n")

        # Streaming
        print("Streaming:")
        for chunk in client.stream_complete("Explain Python in one sentence:"):
            print(chunk, end="", flush=True)
        print("\n")

        # Chat
        chat_response = client.chat_complete(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is machine learning?"}
            ]
        )
        print(f"Chat: {chat_response.content}\n")

    # Example 2: Transformers
    if TRANSFORMERS_AVAILABLE:
        print("=== LLaMA with Transformers ===")

        # Initialize with HuggingFace
        hf_client = LLaMATransformersClient(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            load_in_8bit=True  # Quantization
        )

        # Completion
        hf_response = hf_client.complete(
            "Write a Python function to reverse a string:",
            max_new_tokens=128
        )

        print(f"Response: {hf_response.content}")
        print(f"Tokens/sec: {hf_response.tokens_per_second:.2f}")
