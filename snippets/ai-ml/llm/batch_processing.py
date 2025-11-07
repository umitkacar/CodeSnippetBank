"""
Batch Processing for LLMs
Efficiently process large batches of prompts with rate limiting and parallelization.
"""

import os
import time
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from threading import Semaphore

try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class BatchItem:
    """Container for batch processing item."""
    id: str
    prompt: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BatchResult:
    """Container for batch processing result."""
    id: str
    response: str
    success: bool
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time: float = 0.0


class RateLimiter:
    """Rate limiter using token bucket algorithm."""

    def __init__(self, rate: int, per: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        self.semaphore = Semaphore(rate)

    def acquire(self):
        """Acquire permission to make a request."""
        with self.semaphore:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            self.allowance += time_passed * (self.rate / self.per)

            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                time.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0


class SyncBatchProcessor:
    """Synchronous batch processor with rate limiting."""

    def __init__(
        self,
        process_fn: Callable,
        rate_limit: int = 10,
        max_workers: int = 5,
        retry_attempts: int = 3
    ):
        """
        Initialize batch processor.

        Args:
            process_fn: Function to process each item
            rate_limit: Requests per second
            max_workers: Maximum parallel workers
            retry_attempts: Number of retry attempts on failure
        """
        self.process_fn = process_fn
        self.rate_limiter = RateLimiter(rate=rate_limit)
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts

    def process_item(self, item: BatchItem) -> BatchResult:
        """
        Process a single item with retry logic.

        Args:
            item: Batch item to process

        Returns:
            BatchResult
        """
        start_time = time.time()

        for attempt in range(self.retry_attempts):
            try:
                self.rate_limiter.acquire()

                response = self.process_fn(item.prompt)

                return BatchResult(
                    id=item.id,
                    response=response,
                    success=True,
                    processing_time=time.time() - start_time
                )

            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    return BatchResult(
                        id=item.id,
                        response="",
                        success=False,
                        error=str(e),
                        processing_time=time.time() - start_time
                    )

                # Exponential backoff
                time.sleep(2 ** attempt)

    def process_batch(
        self,
        items: List[BatchItem],
        progress_callback: Optional[Callable] = None
    ) -> List[BatchResult]:
        """
        Process batch of items in parallel.

        Args:
            items: List of items to process
            progress_callback: Optional callback for progress updates

        Returns:
            List of BatchResult objects
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(self.process_item, item): item
                for item in items
            }

            for i, future in enumerate(as_completed(future_to_item), 1):
                result = future.result()
                results.append(result)

                if progress_callback:
                    progress_callback(i, len(items), result)

        return results


class AsyncBatchProcessor:
    """Asynchronous batch processor for better performance."""

    def __init__(
        self,
        async_process_fn: Callable,
        rate_limit: int = 10,
        max_concurrent: int = 10
    ):
        """
        Initialize async batch processor.

        Args:
            async_process_fn: Async function to process items
            rate_limit: Requests per second
            max_concurrent: Maximum concurrent requests
        """
        self.process_fn = async_process_fn
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_item(self, item: BatchItem) -> BatchResult:
        """Process single item asynchronously."""
        async with self.semaphore:
            start_time = time.time()

            try:
                # Rate limiting delay
                await asyncio.sleep(1.0 / self.rate_limit)

                response = await self.process_fn(item.prompt)

                return BatchResult(
                    id=item.id,
                    response=response,
                    success=True,
                    processing_time=time.time() - start_time
                )

            except Exception as e:
                return BatchResult(
                    id=item.id,
                    response="",
                    success=False,
                    error=str(e),
                    processing_time=time.time() - start_time
                )

    async def process_batch(
        self,
        items: List[BatchItem]
    ) -> List[BatchResult]:
        """
        Process batch asynchronously.

        Args:
            items: List of items to process

        Returns:
            List of BatchResult objects
        """
        tasks = [self.process_item(item) for item in items]
        return await asyncio.gather(*tasks)


class ChunkedBatchProcessor:
    """Process large batches in chunks."""

    def __init__(
        self,
        processor: SyncBatchProcessor,
        chunk_size: int = 100
    ):
        """
        Initialize chunked processor.

        Args:
            processor: Batch processor to use
            chunk_size: Size of each chunk
        """
        self.processor = processor
        self.chunk_size = chunk_size

    def process_large_batch(
        self,
        items: List[BatchItem],
        progress_callback: Optional[Callable] = None
    ) -> List[BatchResult]:
        """
        Process large batch in chunks.

        Args:
            items: List of items
            progress_callback: Progress callback

        Returns:
            List of all results
        """
        all_results = []

        for i in range(0, len(items), self.chunk_size):
            chunk = items[i:i + self.chunk_size]

            print(f"Processing chunk {i // self.chunk_size + 1}/{(len(items) - 1) // self.chunk_size + 1}")

            results = self.processor.process_batch(chunk, progress_callback)
            all_results.extend(results)

            # Delay between chunks
            if i + self.chunk_size < len(items):
                time.sleep(1.0)

        return all_results


class OpenAIBatchProcessor:
    """Specialized batch processor for OpenAI."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        rate_limit: int = 10
    ):
        """
        Initialize OpenAI batch processor.

        Args:
            api_key: OpenAI API key
            model: Model to use
            rate_limit: Requests per second
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

        def process_fn(prompt: str) -> str:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        self.processor = SyncBatchProcessor(
            process_fn=process_fn,
            rate_limit=rate_limit
        )

    def process_prompts(
        self,
        prompts: List[str],
        ids: Optional[List[str]] = None
    ) -> List[BatchResult]:
        """
        Process list of prompts.

        Args:
            prompts: List of prompts
            ids: Optional IDs for each prompt

        Returns:
            List of results
        """
        if ids is None:
            ids = [f"item_{i}" for i in range(len(prompts))]

        items = [
            BatchItem(id=id, prompt=prompt)
            for id, prompt in zip(ids, prompts)
        ]

        return self.processor.process_batch(items)


# Usage Examples
if __name__ == "__main__":
    # Example 1: Simple batch processing
    print("=== Sync Batch Processing ===")

    def simple_processor(prompt: str) -> str:
        """Simulate processing."""
        time.sleep(0.1)  # Simulate API call
        return f"Processed: {prompt}"

    processor = SyncBatchProcessor(
        process_fn=simple_processor,
        rate_limit=5,
        max_workers=3
    )

    items = [
        BatchItem(id=f"item_{i}", prompt=f"Prompt {i}")
        for i in range(10)
    ]

    def progress(current, total, result):
        print(f"Progress: {current}/{total} - {result.id}: {result.success}")

    results = processor.process_batch(items, progress_callback=progress)

    successful = sum(1 for r in results if r.success)
    print(f"\nProcessed {successful}/{len(results)} successfully\n")

    # Example 2: Chunked processing
    print("=== Chunked Processing ===")

    chunked = ChunkedBatchProcessor(
        processor=processor,
        chunk_size=5
    )

    large_items = [
        BatchItem(id=f"large_{i}", prompt=f"Prompt {i}")
        for i in range(15)
    ]

    chunked_results = chunked.process_large_batch(large_items)
    print(f"Processed {len(chunked_results)} items in chunks\n")

    # Example 3: Async processing
    print("=== Async Batch Processing ===")

    async def async_processor(prompt: str) -> str:
        """Async processor."""
        await asyncio.sleep(0.1)
        return f"Async processed: {prompt}"

    async def run_async_batch():
        async_proc = AsyncBatchProcessor(
            async_process_fn=async_processor,
            rate_limit=10,
            max_concurrent=5
        )

        async_items = [
            BatchItem(id=f"async_{i}", prompt=f"Prompt {i}")
            for i in range(10)
        ]

        results = await async_proc.process_batch(async_items)
        print(f"Async processed {len(results)} items")

    asyncio.run(run_async_batch())
