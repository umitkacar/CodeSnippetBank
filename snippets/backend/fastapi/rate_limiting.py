"""Rate Limiting Implementation"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import asyncio
import time
from functools import wraps

app = FastAPI()

# In-memory rate limit storage
rate_limit_storage: Dict[str, list] = defaultdict(list)
token_bucket_storage: Dict[str, dict] = {}

# Simple Rate Limiter
class RateLimiter:
    """Simple rate limiter based on sliding window"""

    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.storage: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """Check if request is allowed"""
        current_time = time.time()

        # Remove expired entries
        self.storage[key] = [
            timestamp for timestamp in self.storage[key]
            if current_time - timestamp < self.period
        ]

        # Check limit
        if len(self.storage[key]) >= self.calls:
            oldest = min(self.storage[key])
            retry_after = int(self.period - (current_time - oldest))
            return False, retry_after

        # Add current request
        self.storage[key].append(current_time)
        return True, None

    def get_remaining(self, key: str) -> int:
        """Get remaining calls"""
        current_time = time.time()
        self.storage[key] = [
            timestamp for timestamp in self.storage[key]
            if current_time - timestamp < self.period
        ]
        return max(0, self.calls - len(self.storage[key]))

# Token Bucket Rate Limiter
class TokenBucketRateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.buckets: Dict[str, dict] = {}

    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """Check if request is allowed"""
        current_time = time.time()

        # Initialize bucket if not exists
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.capacity,
                "last_refill": current_time
            }

        bucket = self.buckets[key]

        # Refill tokens
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * self.refill_rate
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Check if token available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, None
        else:
            retry_after = int((1 - bucket["tokens"]) / self.refill_rate)
            return False, retry_after

# Global rate limiters
global_limiter = RateLimiter(calls=100, period=60)
token_bucket_limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1)

# Rate limit decorator
def rate_limit(calls: int, period: int):
    """Decorator for rate limiting"""
    limiter = RateLimiter(calls=calls, period=period)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs or args
            request = kwargs.get("request") or next(
                (arg for arg in args if isinstance(arg, Request)), None
            )

            if request:
                client_ip = request.client.host
                allowed, retry_after = limiter.is_allowed(client_ip)

                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {retry_after} seconds",
                        headers={"Retry-After": str(retry_after)}
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator

# Middleware for global rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Global rate limiting middleware"""
    # Skip rate limiting for certain paths
    if request.url.path in ["/", "/health"]:
        return await call_next(request)

    client_ip = request.client.host
    allowed, retry_after = global_limiter.is_allowed(client_ip)

    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {retry_after} seconds",
                "retry_after": retry_after
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(global_limiter.calls),
                "X-RateLimit-Remaining": "0"
            }
        )

    response = await call_next(request)

    # Add rate limit headers
    remaining = global_limiter.get_remaining(client_ip)
    response.headers["X-RateLimit-Limit"] = str(global_limiter.calls)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + global_limiter.period))

    return response

# Per-user rate limiting
class UserRateLimiter:
    """Rate limiter per user ID"""

    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

    def get_limiter(self, user_id: str, calls: int = 50, period: int = 60) -> RateLimiter:
        """Get or create rate limiter for user"""
        if user_id not in self.limiters:
            self.limiters[user_id] = RateLimiter(calls=calls, period=period)
        return self.limiters[user_id]

user_rate_limiter = UserRateLimiter()

async def check_user_rate_limit(user_id: str, calls: int = 50, period: int = 60):
    """Check rate limit for specific user"""
    limiter = user_rate_limiter.get_limiter(user_id, calls, period)
    allowed, retry_after = limiter.is_allowed(user_id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"User rate limit exceeded. Try again in {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )

# Endpoints
@app.get("/")
async def root():
    return {"message": "Rate limiting demo"}

@app.get("/health")
async def health():
    """Health check endpoint (not rate limited)"""
    return {"status": "healthy"}

@app.get("/api/data")
@rate_limit(calls=10, period=60)
async def get_data(request: Request):
    """Endpoint with decorator rate limiting"""
    return {
        "message": "Data retrieved successfully",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/user-data/{user_id}")
async def get_user_data(user_id: str):
    """Endpoint with per-user rate limiting"""
    await check_user_rate_limit(user_id, calls=20, period=60)

    return {
        "user_id": user_id,
        "data": "User specific data",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/expensive-operation")
@rate_limit(calls=5, period=300)  # 5 calls per 5 minutes
async def expensive_operation(request: Request):
    """Endpoint with strict rate limiting"""
    await asyncio.sleep(1)  # Simulate expensive operation

    return {
        "message": "Expensive operation completed",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/token-bucket")
async def token_bucket_endpoint(request: Request):
    """Endpoint using token bucket rate limiting"""
    client_ip = request.client.host
    allowed, retry_after = token_bucket_limiter.is_allowed(client_ip)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )

    return {
        "message": "Request successful",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/rate-limit-info")
async def rate_limit_info(request: Request):
    """Get rate limit information"""
    client_ip = request.client.host
    remaining = global_limiter.get_remaining(client_ip)

    return {
        "limit": global_limiter.calls,
        "remaining": remaining,
        "period": global_limiter.period,
        "reset_in": global_limiter.period
    }

# Adaptive rate limiting based on server load
class AdaptiveRateLimiter:
    """Rate limiter that adjusts based on server load"""

    def __init__(self, min_calls: int, max_calls: int, period: int):
        self.min_calls = min_calls
        self.max_calls = max_calls
        self.period = period
        self.current_calls = max_calls
        self.limiter = RateLimiter(calls=self.current_calls, period=period)

    def adjust_limit(self, server_load: float):
        """Adjust rate limit based on server load (0.0 to 1.0)"""
        if server_load > 0.8:
            self.current_calls = self.min_calls
        elif server_load > 0.5:
            self.current_calls = int(self.min_calls + (self.max_calls - self.min_calls) * 0.5)
        else:
            self.current_calls = self.max_calls

        self.limiter = RateLimiter(calls=self.current_calls, period=self.period)

adaptive_limiter = AdaptiveRateLimiter(min_calls=10, max_calls=100, period=60)

@app.get("/api/adaptive")
async def adaptive_endpoint(request: Request):
    """Endpoint with adaptive rate limiting"""
    # Simulate getting server load
    server_load = 0.3  # In production, get actual server load

    adaptive_limiter.adjust_limit(server_load)

    client_ip = request.client.host
    allowed, retry_after = adaptive_limiter.limiter.is_allowed(client_ip)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds"
        )

    return {
        "message": "Request successful",
        "current_limit": adaptive_limiter.current_calls,
        "server_load": server_load
    }
