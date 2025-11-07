"""Redis Caching Integration"""
from fastapi import FastAPI, Depends
import json
from typing import Optional, Any

app = FastAPI()

class RedisCache:
    """Redis cache wrapper"""

    def __init__(self):
        self.cache = {}  # Simulated Redis

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        return self.cache.get(key)

    async def set(self, key: str, value: Any, expire: int = 300):
        """Set value in cache"""
        self.cache[key] = json.dumps(value)

    async def delete(self, key: str):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]

redis = RedisCache()

async def get_redis():
    """Redis dependency"""
    return redis

@app.get("/cached-data/{key}")
async def get_cached_data(key: str, cache: RedisCache = Depends(get_redis)):
    """Get data with Redis caching"""
    cached = await cache.get(key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    # Simulate database query
    data = {"key": key, "value": f"data for {key}"}
    await cache.set(key, data)

    return {"source": "database", "data": data}

@app.delete("/cache/{key}")
async def invalidate_cache(key: str, cache: RedisCache = Depends(get_redis)):
    """Invalidate cache entry"""
    await cache.delete(key)
    return {"message": f"Cache for {key} invalidated"}
