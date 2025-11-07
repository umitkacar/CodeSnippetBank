"""Custom Middleware Implementation"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
import time
import logging
from typing import Callable

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com", "localhost", "127.0.0.1"]
)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production"
)

# Custom Timing Middleware
class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to measure request processing time"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add custom header with processing time
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.4f}s"
        )

        return response

app.add_middleware(TimingMiddleware)

# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import uuid

        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

app.add_middleware(RequestIDMiddleware)

# Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}"
        )

        # Process request
        response = await call_next(request)

        # Log response
        logger.info(
            f"Response: {response.status_code} for "
            f"{request.method} {request.url.path}"
        )

        return response

app.add_middleware(LoggingMiddleware)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

app.add_middleware(SecurityHeadersMiddleware)

# Rate Limit Tracking Middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                timestamp for timestamp in self.clients[client_ip]
                if current_time - timestamp < self.period
            ]

        # Check rate limit
        if client_ip not in self.clients:
            self.clients[client_ip] = []

        if len(self.clients[client_ip]) >= self.calls:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(self.period)}
            )

        # Add current request
        self.clients[client_ip].append(current_time)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(
            self.calls - len(self.clients[client_ip])
        )

        return response

# app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Authentication Middleware
class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Custom authentication middleware"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for public endpoints
        public_paths = ["/", "/health", "/docs", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)

        # Check for API key
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return Response(
                content="Missing API Key",
                status_code=401,
                headers={"WWW-Authenticate": "API-Key"}
            )

        # Validate API key (in production, check against database)
        if api_key != "valid-api-key":
            return Response(
                content="Invalid API Key",
                status_code=401
            )

        # Proceed with request
        response = await call_next(request)
        return response

# app.add_middleware(AuthenticationMiddleware)

# Error Handling Middleware
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catch and handle errors"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)

            return Response(
                content=f"Internal server error: {str(e)}",
                status_code=500
            )

app.add_middleware(ErrorHandlingMiddleware)

# Test endpoints
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/slow")
async def slow_endpoint():
    """Endpoint to test timing middleware"""
    import asyncio
    await asyncio.sleep(2)
    return {"message": "Slow response"}

@app.get("/request-info")
async def request_info(request: Request):
    """Get request information"""
    return {
        "request_id": getattr(request.state, "request_id", None),
        "client_host": request.client.host,
        "method": request.method,
        "path": request.url.path
    }
