"""Async Operations and Concurrency"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
import asyncio
import aiohttp
import time

app = FastAPI()

# Models
class URLCheck(BaseModel):
    url: str
    status_code: int
    response_time: float
    success: bool

class BatchURLRequest(BaseModel):
    urls: List[str]

# Async HTTP request
async def check_url(url: str) -> URLCheck:
    """Check URL availability asynchronously"""
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_time = time.time() - start_time
                return URLCheck(
                    url=url,
                    status_code=response.status,
                    response_time=response_time,
                    success=response.status == 200
                )
    except Exception as e:
        response_time = time.time() - start_time
        return URLCheck(
            url=url,
            status_code=0,
            response_time=response_time,
            success=False
        )

@app.post("/check-urls", response_model=List[URLCheck])
async def check_multiple_urls(request: BatchURLRequest):
    """Check multiple URLs concurrently"""
    tasks = [check_url(url) for url in request.urls]
    results = await asyncio.gather(*tasks)
    return results

# Async database simulation
async def fetch_user_data(user_id: int):
    """Simulate async database query"""
    await asyncio.sleep(0.5)  # Simulate DB query
    return {"user_id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

async def fetch_user_orders(user_id: int):
    """Simulate async database query for orders"""
    await asyncio.sleep(0.3)
    return [
        {"order_id": i, "user_id": user_id, "total": 100.0 * i}
        for i in range(1, 4)
    ]

async def fetch_user_profile(user_id: int):
    """Simulate async database query for profile"""
    await asyncio.sleep(0.2)
    return {"user_id": user_id, "bio": "User bio", "avatar": "avatar.jpg"}

@app.get("/users/{user_id}/complete")
async def get_user_complete_data(user_id: int):
    """Fetch user data from multiple sources concurrently"""
    # Run all queries concurrently
    user_data, orders, profile = await asyncio.gather(
        fetch_user_data(user_id),
        fetch_user_orders(user_id),
        fetch_user_profile(user_id)
    )

    return {
        "user": user_data,
        "orders": orders,
        "profile": profile
    }

# Async file processing
async def process_file_async(filename: str):
    """Simulate async file processing"""
    await asyncio.sleep(2)
    return {"filename": filename, "status": "processed", "lines": 100}

@app.post("/process-files")
async def process_multiple_files(filenames: List[str]):
    """Process multiple files concurrently"""
    tasks = [process_file_async(filename) for filename in filenames]
    results = await asyncio.gather(*tasks)
    return {"results": results, "total": len(results)}

# Async with timeout
async def long_running_task(duration: int):
    """Simulate long running task"""
    await asyncio.sleep(duration)
    return {"duration": duration, "result": "completed"}

@app.get("/task-with-timeout/{duration}")
async def task_with_timeout(duration: int):
    """Execute task with timeout"""
    try:
        result = await asyncio.wait_for(
            long_running_task(duration),
            timeout=5.0
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Task timed out")

# Async streaming
async def generate_numbers(count: int):
    """Generate numbers asynchronously"""
    for i in range(count):
        await asyncio.sleep(0.1)
        yield i

@app.get("/stream-numbers/{count}")
async def stream_numbers(count: int):
    """Stream numbers"""
    numbers = []
    async for num in generate_numbers(count):
        numbers.append(num)
    return {"numbers": numbers}

# Concurrent API calls
async def fetch_api_data(endpoint: str):
    """Fetch data from API endpoint"""
    await asyncio.sleep(0.5)
    return {"endpoint": endpoint, "data": f"Data from {endpoint}"}

@app.get("/aggregate-data")
async def aggregate_multiple_apis():
    """Aggregate data from multiple API endpoints concurrently"""
    endpoints = ["users", "posts", "comments", "products"]

    tasks = [fetch_api_data(endpoint) for endpoint in endpoints]
    results = await asyncio.gather(*tasks)

    return {
        "results": results,
        "timestamp": time.time()
    }

# Async retry logic
async def unreliable_operation(attempt: int):
    """Simulate unreliable operation"""
    if attempt < 3:
        raise Exception(f"Operation failed on attempt {attempt}")
    return {"success": True, "attempt": attempt}

async def retry_async(func, max_retries: int = 3, delay: float = 1.0):
    """Retry async function"""
    for attempt in range(1, max_retries + 1):
        try:
            return await func(attempt)
        except Exception as e:
            if attempt == max_retries:
                raise HTTPException(
                    status_code=500,
                    detail=f"Operation failed after {max_retries} attempts"
                )
            await asyncio.sleep(delay)

@app.get("/retry-operation")
async def retry_operation():
    """Operation with retry logic"""
    result = await retry_async(unreliable_operation, max_retries=5)
    return result
