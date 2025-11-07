"""
Bearer Token Authentication
Production-ready Bearer token implementation for API authentication
"""
from typing import Optional, Callable, Dict
from functools import wraps
import re


class BearerTokenAuth:
    """Bearer token authentication handler"""

    def __init__(self, token_validator: Callable[[str], Optional[Dict]]):
        """
        Initialize bearer token auth

        Args:
            token_validator: Function to validate token and return user data
        """
        self.token_validator = token_validator

    def extract_token(self, authorization_header: Optional[str]) -> Optional[str]:
        """
        Extract bearer token from Authorization header

        Args:
            authorization_header: Authorization header value

        Returns:
            Token string or None
        """
        if not authorization_header:
            return None

        # Bearer token format: "Bearer <token>"
        match = re.match(r'^Bearer\s+(.+)$', authorization_header, re.IGNORECASE)

        if match:
            return match.group(1)

        return None

    def authenticate(self, authorization_header: Optional[str]) -> Optional[Dict]:
        """
        Authenticate request using bearer token

        Args:
            authorization_header: Authorization header value

        Returns:
            User data if authenticated, None otherwise
        """
        token = self.extract_token(authorization_header)

        if not token:
            return None

        # Validate token
        return self.token_validator(token)

    def require_auth(self, func):
        """
        Decorator to require authentication

        Usage:
            @auth.require_auth
            def protected_route(user):
                return f"Hello {user['username']}"
        """
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            user = self.authenticate(auth_header)

            if not user:
                return {'error': 'Unauthorized'}, 401

            return func(user, *args, **kwargs)

        return wrapper

    def require_scope(self, required_scope: str):
        """
        Decorator to require specific scope

        Args:
            required_scope: Required permission scope

        Usage:
            @auth.require_scope('admin')
            def admin_route(user):
                return "Admin panel"
        """
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                auth_header = request.headers.get('Authorization')
                user = self.authenticate(auth_header)

                if not user:
                    return {'error': 'Unauthorized'}, 401

                user_scopes = user.get('scopes', [])
                if required_scope not in user_scopes:
                    return {'error': 'Forbidden'}, 403

                return func(user, *args, **kwargs)

            return wrapper
        return decorator


class APITokenMiddleware:
    """Middleware for API token authentication"""

    def __init__(self, token_auth: BearerTokenAuth):
        """
        Initialize middleware

        Args:
            token_auth: BearerTokenAuth instance
        """
        self.token_auth = token_auth

    def process_request(self, request) -> Optional[Dict]:
        """
        Process incoming request for authentication

        Args:
            request: HTTP request object

        Returns:
            Error response or None to continue
        """
        # Skip authentication for public endpoints
        public_paths = ['/health', '/login', '/register']

        if request.path in public_paths:
            return None

        # Authenticate request
        auth_header = request.headers.get('Authorization')
        user = self.token_auth.authenticate(auth_header)

        if not user:
            return {
                'error': 'Unauthorized',
                'message': 'Valid authentication required'
            }, 401

        # Attach user to request
        request.user = user
        return None


# Example usage with Flask
def create_flask_bearer_auth():
    """Example Flask implementation"""
    from flask import request, jsonify

    # Token validator function
    def validate_token(token: str) -> Optional[Dict]:
        # In production, validate JWT or query database
        # This is a simple example
        valid_tokens = {
            'secret_token_123': {
                'user_id': 1,
                'username': 'john_doe',
                'scopes': ['read', 'write', 'admin']
            }
        }
        return valid_tokens.get(token)

    auth = BearerTokenAuth(validate_token)

    @auth.require_auth
    def protected_route(user):
        return jsonify({
            'message': f"Hello {user['username']}",
            'user_id': user['user_id']
        })

    @auth.require_scope('admin')
    def admin_route(user):
        return jsonify({'message': 'Admin panel'})

    return auth, protected_route, admin_route


# Example usage with FastAPI
def create_fastapi_bearer_auth():
    """Example FastAPI implementation"""
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

    security = HTTPBearer()

    def validate_token(token: str) -> Optional[Dict]:
        # Token validation logic
        valid_tokens = {
            'secret_token_123': {
                'user_id': 1,
                'username': 'john_doe',
                'scopes': ['read', 'write', 'admin']
            }
        }
        return valid_tokens.get(token)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """Dependency for authentication"""
        user = validate_token(credentials.credentials)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    async def require_scope(required_scope: str):
        """Dependency for scope validation"""
        def scope_checker(user: Dict = Depends(get_current_user)) -> Dict:
            if required_scope not in user.get('scopes', []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return user
        return scope_checker

    return get_current_user, require_scope


if __name__ == "__main__":
    # Simple example
    def simple_validator(token: str) -> Optional[Dict]:
        if token == "valid_token":
            return {'user_id': 1, 'username': 'test_user', 'scopes': ['read']}
        return None

    auth = BearerTokenAuth(simple_validator)

    # Test token extraction
    token = auth.extract_token("Bearer valid_token")
    print(f"Extracted token: {token}")

    # Test authentication
    user = auth.authenticate("Bearer valid_token")
    print(f"Authenticated user: {user}")

    # Test invalid token
    user = auth.authenticate("Bearer invalid_token")
    print(f"Invalid auth result: {user}")
