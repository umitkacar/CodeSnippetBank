"""Caching Strategies"""
from fastapi import FastAPI, Depends, Response, Request
from pydantic import BaseModel
from typing import Optional, Any
import hashlib
import json
import time
from functools import wraps
from datetime import datetime, timedelta

app = FastAPI()

# Simple in-memory cache
class SimpleCache:
    """Simple in-memory cache"""

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item["expires_at"]:
                return item["value"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL in seconds"""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }

    def delete(self, key: str):
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Clear all cache"""
        self._cache.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None

cache = SimpleCache()

# Cache decorator
def cache_response(ttl: int = 300):
    """Decorator to cache endpoint responses"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            request = kwargs.get("request")
            if request:
                cache_key = f"{func.__name__}:{request.url.path}:{request.url.query}"
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator

# Models
class DataModel(BaseModel):
    id: int
    value: str
    timestamp: datetime

# Cached endpoints
@app.get("/cached-data/{item_id}")
@cache_response(ttl=60)
async def get_cached_data(item_id: int, request: Request):
    """Get data with caching"""
    # Simulate expensive operation
    time.sleep(1)

    return DataModel(
        id=item_id,
        value=f"Data for item {item_id}",
        timestamp=datetime.utcnow()
    )

@app.get("/expensive-operation")
@cache_response(ttl=300)
async def expensive_operation(request: Request):
    """Expensive operation with caching"""
    time.sleep(2)

    return {
        "result": "Expensive computation result",
        "computed_at": datetime.utcnow().isoformat()
    }

# Manual cache control
@app.get("/manual-cache/{key}")
async def get_manual_cache(key: str):
    """Get value from cache manually"""
    value = cache.get(key)
    if value is None:
        return {"error": "Key not found in cache"}

    return {"key": key, "value": value}

@app.post("/manual-cache/{key}")
async def set_manual_cache(key: str, value: str, ttl: int = 300):
    """Set value in cache manually"""
    cache.set(key, value, ttl)
    return {"message": "Value cached successfully", "key": key, "ttl": ttl}

@app.delete("/manual-cache/{key}")
async def delete_manual_cache(key: str):
    """Delete value from cache"""
    cache.delete(key)
    return {"message": "Value deleted from cache", "key": key}

@app.post("/cache/clear")
async def clear_cache():
    """Clear all cache"""
    cache.clear()
    return {"message": "Cache cleared successfully"}

# ETags for conditional requests
def generate_etag(data: Any) -> str:
    """Generate ETag from data"""
    content = json.dumps(data, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

@app.get("/data-with-etag/{item_id}")
async def get_data_with_etag(item_id: int, request: Request, response: Response):
    """Get data with ETag support"""
    data = {
        "id": item_id,
        "value": f"Data for item {item_id}",
        "timestamp": datetime.utcnow().isoformat()
    }

    etag = generate_etag(data)

    # Check If-None-Match header
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match == etag:
        response.status_code = 304
        return None

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "max-age=300"

    return data

# Cache invalidation
class CacheInvalidator:
    """Cache invalidation helper"""

    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalidate all cache keys matching pattern"""
        keys_to_delete = [
            key for key in cache._cache.keys()
            if pattern in key
        ]
        for key in keys_to_delete:
            cache.delete(key)
        return len(keys_to_delete)

@app.post("/invalidate-cache")
async def invalidate_cache(pattern: str):
    """Invalidate cache by pattern"""
    count = CacheInvalidator.invalidate_pattern(pattern)
    return {
        "message": f"Invalidated {count} cache entries",
        "pattern": pattern
    }

# Response headers for caching
@app.get("/with-cache-headers/{item_id}")
async def get_with_cache_headers(item_id: int, response: Response):
    """Get data with cache control headers"""
    data = {
        "id": item_id,
        "value": f"Data for item {item_id}",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Set cache control headers
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["Expires"] = (
        datetime.utcnow() + timedelta(seconds=300)
    ).strftime("%a, %d %b %Y %H:%M:%S GMT")

    return data

# LRU Cache implementation
from collections import OrderedDict

class LRUCache:
    """LRU Cache implementation"""

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> Optional[Any]:
        """Get value and move to end (most recently used)"""
        if key not in self.cache:
            return None

        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: Any):
        """Set value"""
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

lru_cache = LRUCache(capacity=100)

@app.get("/lru-cached/{key}")
async def get_lru_cached(key: str):
    """Get value from LRU cache"""
    value = lru_cache.get(key)
    if value is None:
        return {"error": "Key not found in cache"}

    return {"key": key, "value": value}

@app.post("/lru-cached/{key}")
async def set_lru_cached(key: str, value: str):
    """Set value in LRU cache"""
    lru_cache.set(key, value)
    return {"message": "Value cached successfully", "key": key}
