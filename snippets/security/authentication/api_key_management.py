"""
API Key Management
Production-ready API key generation, validation, and rate limiting
"""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
import json


@dataclass
class APIKey:
    """API Key data structure"""
    key_id: str
    key_hash: str
    name: str
    user_id: int
    scopes: List[str]
    created_at: str
    expires_at: Optional[str]
    last_used: Optional[str]
    is_active: bool


class APIKeyManager:
    """Manage API keys with secure generation and validation"""

    def __init__(self, pepper: str):
        """
        Initialize API key manager

        Args:
            pepper: Secret pepper for additional security
        """
        self.pepper = pepper

    def generate_api_key(self) -> tuple[str, str]:
        """
        Generate a new API key

        Returns:
            Tuple of (key_id, api_key)
            key_id is public identifier, api_key is the secret
        """
        # Generate key ID (public)
        key_id = f"ak_{secrets.token_urlsafe(16)}"

        # Generate secret key (64 bytes = 512 bits)
        api_key = f"sk_{secrets.token_urlsafe(48)}"

        return key_id, api_key

    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for secure storage

        Args:
            api_key: Plain API key

        Returns:
            Hashed key
        """
        # Use HMAC-SHA256 with pepper
        hashed = hmac.new(
            self.pepper.encode(),
            api_key.encode(),
            hashlib.sha256
        ).hexdigest()

        return hashed

    def create_api_key(
        self,
        user_id: int,
        name: str,
        scopes: List[str],
        expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """
        Create a new API key

        Args:
            user_id: User ID
            name: Key name/description
            scopes: List of permissions
            expires_in_days: Optional expiration in days

        Returns:
            Tuple of (plain_api_key, APIKey object)
        """
        key_id, api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)

        expires_at = None
        if expires_in_days:
            expires_at = (
                datetime.utcnow() + timedelta(days=expires_in_days)
            ).isoformat()

        api_key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            scopes=scopes,
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
            last_used=None,
            is_active=True
        )

        return api_key, api_key_obj

    def verify_api_key(
        self,
        api_key: str,
        stored_key: APIKey
    ) -> bool:
        """
        Verify API key

        Args:
            api_key: Plain API key from request
            stored_key: Stored APIKey object

        Returns:
            True if valid
        """
        # Check if active
        if not stored_key.is_active:
            return False

        # Check expiration
        if stored_key.expires_at:
            expires = datetime.fromisoformat(stored_key.expires_at)
            if datetime.utcnow() > expires:
                return False

        # Verify hash
        provided_hash = self.hash_api_key(api_key)
        return secrets.compare_digest(provided_hash, stored_key.key_hash)

    def has_scope(self, api_key: APIKey, required_scope: str) -> bool:
        """
        Check if API key has required scope

        Args:
            api_key: APIKey object
            required_scope: Required scope

        Returns:
            True if scope present
        """
        return required_scope in api_key.scopes

    def rotate_api_key(
        self,
        old_key: APIKey
    ) -> tuple[str, APIKey]:
        """
        Rotate an API key (generate new, keep same metadata)

        Args:
            old_key: Existing APIKey object

        Returns:
            Tuple of (new_plain_key, new_APIKey)
        """
        return self.create_api_key(
            user_id=old_key.user_id,
            name=old_key.name,
            scopes=old_key.scopes,
            expires_in_days=None
        )


class APIKeyRateLimiter:
    """Rate limiting for API keys"""

    def __init__(self, redis_client):
        """
        Initialize rate limiter

        Args:
            redis_client: Redis client for storing counts
        """
        self.redis = redis_client

    def check_rate_limit(
        self,
        key_id: str,
        limit: int = 1000,
        window: int = 3600
    ) -> tuple[bool, Dict]:
        """
        Check rate limit for API key

        Args:
            key_id: API key ID
            limit: Maximum requests per window
            window: Time window in seconds

        Returns:
            Tuple of (allowed, rate_limit_info)
        """
        current_time = int(datetime.utcnow().timestamp())
        window_start = current_time - window

        # Redis key for this API key
        redis_key = f"ratelimit:{key_id}"

        # Remove old entries
        self.redis.zremrangebyscore(redis_key, 0, window_start)

        # Count requests in current window
        current_count = self.redis.zcard(redis_key)

        rate_limit_info = {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset": current_time + window,
            "used": current_count
        }

        if current_count >= limit:
            return False, rate_limit_info

        # Add current request
        self.redis.zadd(redis_key, {str(current_time): current_time})
        self.redis.expire(redis_key, window)

        rate_limit_info["remaining"] -= 1
        rate_limit_info["used"] += 1

        return True, rate_limit_info


class APIKeyStore:
    """Simple in-memory API key store (use database in production)"""

    def __init__(self):
        self.keys: Dict[str, APIKey] = {}

    def save(self, api_key: APIKey) -> None:
        """Save API key"""
        self.keys[api_key.key_id] = api_key

    def get_by_id(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        return self.keys.get(key_id)

    def list_user_keys(self, user_id: int) -> List[APIKey]:
        """List all keys for a user"""
        return [k for k in self.keys.values() if k.user_id == user_id]

    def revoke(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.keys:
            self.keys[key_id].is_active = False
            return True
        return False


# Example usage
if __name__ == "__main__":
    # Initialize manager
    key_manager = APIKeyManager(pepper="super_secret_pepper_value")

    # Create API key
    plain_key, api_key_obj = key_manager.create_api_key(
        user_id=123,
        name="Production API Key",
        scopes=["read", "write", "admin"],
        expires_in_days=365
    )

    print(f"Generated API Key: {plain_key}")
    print(f"Key ID: {api_key_obj.key_id}")
    print(f"Scopes: {api_key_obj.scopes}")

    # Store key
    store = APIKeyStore()
    store.save(api_key_obj)

    # Verify key
    is_valid = key_manager.verify_api_key(plain_key, api_key_obj)
    print(f"Key valid: {is_valid}")

    # Check scope
    has_admin = key_manager.has_scope(api_key_obj, "admin")
    print(f"Has admin scope: {has_admin}")

    # List user keys
    user_keys = store.list_user_keys(123)
    print(f"User has {len(user_keys)} keys")
