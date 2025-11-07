"""Dependency Injection Patterns"""
from fastapi import Depends, FastAPI, HTTPException, status, Header, Query
from typing import Optional, Annotated
from pydantic import BaseModel
import time

app = FastAPI()

# Database dependency
class Database:
    """Simulated database connection"""

    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        print("Database connected")

    def disconnect(self):
        self.connected = False
        print("Database disconnected")

    def query(self, sql: str):
        if not self.connected:
            raise Exception("Database not connected")
        return f"Results for: {sql}"

async def get_db():
    """Database dependency"""
    db = Database()
    try:
        db.connect()
        yield db
    finally:
        db.disconnect()

# Configuration dependency
class Settings:
    """Application settings"""

    def __init__(self):
        self.app_name = "My FastAPI App"
        self.admin_email = "admin@example.com"
        self.items_per_page = 50
        self.api_version = "1.0.0"

def get_settings():
    """Settings dependency"""
    return Settings()

# Authentication dependencies
async def get_token(authorization: str = Header(...)):
    """Extract token from header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme"
        )
    return authorization.replace("Bearer ", "")

async def verify_token(token: str = Depends(get_token)):
    """Verify token validity"""
    if token != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return token

async def get_current_user(token: str = Depends(verify_token)):
    """Get current user from token"""
    # In production, decode JWT and fetch user from database
    return {
        "id": "user_123",
        "username": "johndoe",
        "email": "johndoe@example.com"
    }

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """Check if user is active"""
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Admin user dependency
async def get_admin_user(
    current_user: dict = Depends(get_current_active_user)
):
    """Check if user is admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Pagination dependency
class Pagination:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit

# Query parameters dependency
class CommonQueryParams:
    def __init__(
        self,
        q: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        order: str = "asc"
    ):
        self.q = q
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.order = order

# Service layer dependency
class ItemService:
    """Item service with business logic"""

    def __init__(self, db: Database = Depends(get_db)):
        self.db = db

    def get_items(self, skip: int = 0, limit: int = 100):
        """Get items from database"""
        sql = f"SELECT * FROM items LIMIT {limit} OFFSET {skip}"
        return self.db.query(sql)

    def create_item(self, item_data: dict):
        """Create new item"""
        sql = f"INSERT INTO items VALUES {item_data}"
        return self.db.query(sql)

# Caching dependency
class Cache:
    """Simple cache implementation"""

    def __init__(self):
        self._cache = {}

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value, ttl: int = 60):
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }

    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

cache = Cache()

def get_cache():
    """Cache dependency"""
    return cache

# API Endpoints
@app.get("/items/")
async def read_items(
    commons: Annotated[CommonQueryParams, Depends()],
    db: Database = Depends(get_db)
):
    """Get items with common query parameters"""
    items = db.query(f"SELECT * FROM items WHERE name LIKE '%{commons.q}%'")
    return {
        "query": commons.q,
        "skip": commons.skip,
        "limit": commons.limit,
        "items": items
    }

@app.get("/items-paginated/")
async def read_items_paginated(
    pagination: Pagination = Depends(),
    db: Database = Depends(get_db)
):
    """Get items with pagination"""
    items = db.query(f"SELECT * FROM items LIMIT {pagination.limit} OFFSET {pagination.skip}")
    return {
        "skip": pagination.skip,
        "limit": pagination.limit,
        "items": items
    }

@app.get("/users/me")
async def read_user_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user (requires authentication)"""
    return current_user

@app.get("/admin/users")
async def read_all_users(
    admin_user: dict = Depends(get_admin_user),
    db: Database = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query("SELECT * FROM users")
    return {"users": users, "admin": admin_user}

@app.get("/settings/")
async def read_settings(settings: Settings = Depends(get_settings)):
    """Get application settings"""
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page,
        "api_version": settings.api_version
    }

@app.get("/items-service/")
async def read_items_service(
    item_service: ItemService = Depends(),
    pagination: Pagination = Depends()
):
    """Get items using service layer"""
    items = item_service.get_items(pagination.skip, pagination.limit)
    return {"items": items}

@app.get("/cached-data/")
async def read_cached_data(
    key: str,
    cache: Cache = Depends(get_cache)
):
    """Get cached data"""
    data = cache.get(key)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data not found in cache"
        )
    return {"key": key, "data": data}

@app.post("/cache/")
async def set_cache_data(
    key: str,
    value: str,
    ttl: int = 60,
    cache: Cache = Depends(get_cache)
):
    """Set cache data"""
    cache.set(key, value, ttl)
    return {"message": "Data cached successfully", "key": key, "ttl": ttl}

# Nested dependencies example
async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key"""
    if x_api_key != "secret-api-key":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return x_api_key

async def get_authenticated_service(
    api_key: str = Depends(verify_api_key),
    db: Database = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """Get service with multiple dependencies"""
    return {
        "api_key": api_key,
        "db": db,
        "settings": settings
    }

@app.get("/protected-resource/")
async def read_protected_resource(
    service: dict = Depends(get_authenticated_service)
):
    """Access protected resource with nested dependencies"""
    return {
        "message": "Access granted",
        "app_name": service["settings"].app_name
    }
