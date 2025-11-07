"""Security Best Practices"""
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBasic, HTTPBearer, APIKeyHeader, APIKeyQuery
from pydantic import BaseModel
from typing import Optional
import secrets

app = FastAPI()

# Security schemes
security_basic = HTTPBasic()
security_bearer = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key")
api_key_query = APIKeyQuery(name="api_key")

# Credentials
VALID_API_KEYS = {"secret-api-key-123", "another-key-456"}
VALID_TOKENS = {"valid-bearer-token"}

# API Key authentication
async def verify_api_key_header(api_key: str = Security(api_key_header)):
    """Verify API key from header"""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

async def verify_api_key_query(api_key: str = Security(api_key_query)):
    """Verify API key from query parameter"""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Bearer token authentication
async def verify_bearer_token(credentials = Security(security_bearer)):
    """Verify bearer token"""
    if credentials.credentials not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return credentials.credentials

# Protected endpoints
@app.get("/protected/api-key-header")
async def protected_api_key_header(api_key: str = Depends(verify_api_key_header)):
    """Protected with API key in header"""
    return {"message": "Access granted", "api_key": api_key}

@app.get("/protected/api-key-query")
async def protected_api_key_query(api_key: str = Depends(verify_api_key_query)):
    """Protected with API key in query"""
    return {"message": "Access granted"}

@app.get("/protected/bearer")
async def protected_bearer(token: str = Depends(verify_bearer_token)):
    """Protected with bearer token"""
    return {"message": "Access granted"}

# CSRF protection
class CSRFToken(BaseModel):
    token: str

csrf_tokens = set()

@app.get("/csrf-token", response_model=CSRFToken)
async def get_csrf_token():
    """Get CSRF token"""
    token = secrets.token_urlsafe(32)
    csrf_tokens.add(token)
    return CSRFToken(token=token)

@app.post("/protected/csrf")
async def protected_csrf(
    data: dict,
    csrf_token: str = Security(APIKeyHeader(name="X-CSRF-Token"))
):
    """Protected with CSRF token"""
    if csrf_token not in csrf_tokens:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    csrf_tokens.remove(csrf_token)  # Single use
    return {"message": "Operation successful", "data": data}

# Input sanitization
import html
import re

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # HTML escape
    text = html.escape(text)
    # Remove potentially dangerous characters
    text = re.sub(r'[<>\"\'&]', '', text)
    return text

@app.post("/safe-input")
async def safe_input(text: str):
    """Endpoint with input sanitization"""
    sanitized = sanitize_input(text)
    return {"original": text, "sanitized": sanitized}

# Rate limiting per API key
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.period
        ]
        if len(self.requests[key]) >= self.calls:
            return False
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter(calls=10, period=60)

@app.get("/protected/rate-limited")
async def rate_limited(api_key: str = Depends(verify_api_key_header)):
    """Protected with rate limiting"""
    if not rate_limiter.is_allowed(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    return {"message": "Access granted"}
