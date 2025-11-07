"""
Token Refresh and Rotation Strategy
Production-ready refresh token implementation with rotation
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
import json


@dataclass
class TokenPair:
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    access_token_expires: str
    refresh_token_expires: str
    token_type: str = "Bearer"


@dataclass
class RefreshTokenData:
    """Refresh token metadata"""
    token_hash: str
    user_id: int
    family_id: str  # For rotation detection
    created_at: str
    expires_at: str
    is_revoked: bool
    parent_token: Optional[str]  # Previous token in rotation chain


class RefreshTokenManager:
    """Manage refresh tokens with automatic rotation"""

    def __init__(
        self,
        jwt_manager,
        access_token_lifetime: int = 900,  # 15 minutes
        refresh_token_lifetime: int = 2592000  # 30 days
    ):
        """
        Initialize refresh token manager

        Args:
            jwt_manager: JWT manager instance
            access_token_lifetime: Access token lifetime in seconds
            refresh_token_lifetime: Refresh token lifetime in seconds
        """
        self.jwt_manager = jwt_manager
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime
        self.token_store: Dict[str, RefreshTokenData] = {}

    def generate_refresh_token(self) -> str:
        """
        Generate cryptographically secure refresh token

        Returns:
            Refresh token string
        """
        return secrets.token_urlsafe(64)

    def hash_token(self, token: str) -> str:
        """
        Hash refresh token for storage

        Args:
            token: Plain refresh token

        Returns:
            Hashed token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def create_token_pair(
        self,
        user_id: int,
        user_data: Dict,
        family_id: Optional[str] = None,
        parent_token: Optional[str] = None
    ) -> TokenPair:
        """
        Create new access and refresh token pair

        Args:
            user_id: User ID
            user_data: User data for access token
            family_id: Token family ID (for rotation)
            parent_token: Parent refresh token (if rotating)

        Returns:
            TokenPair object
        """
        # Generate access token
        access_token_data = {**user_data, "user_id": user_id}
        access_token = self.jwt_manager.create_access_token(
            access_token_data,
            expires_delta=timedelta(seconds=self.access_token_lifetime)
        )

        # Generate refresh token
        refresh_token = self.generate_refresh_token()
        token_hash = self.hash_token(refresh_token)

        # Create or reuse family ID
        if not family_id:
            family_id = secrets.token_urlsafe(16)

        # Store refresh token metadata
        now = datetime.utcnow()
        expires = now + timedelta(seconds=self.refresh_token_lifetime)

        refresh_data = RefreshTokenData(
            token_hash=token_hash,
            user_id=user_id,
            family_id=family_id,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            is_revoked=False,
            parent_token=self.hash_token(parent_token) if parent_token else None
        )

        self.token_store[token_hash] = refresh_data

        # Create token pair
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires=(
                now + timedelta(seconds=self.access_token_lifetime)
            ).isoformat(),
            refresh_token_expires=expires.isoformat()
        )

    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[Tuple[TokenPair, bool]]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            Tuple of (new TokenPair, is_rotation_detected) or None if invalid
        """
        token_hash = self.hash_token(refresh_token)
        refresh_data = self.token_store.get(token_hash)

        if not refresh_data:
            # Token not found - might be reuse attack
            return None

        # Check if revoked
        if refresh_data.is_revoked:
            # Possible token reuse - revoke entire family
            self._revoke_token_family(refresh_data.family_id)
            return None, True

        # Check expiration
        expires = datetime.fromisoformat(refresh_data.expires_at)
        if datetime.utcnow() > expires:
            return None

        # Revoke current refresh token
        refresh_data.is_revoked = True

        # Get user data for new access token
        user_data = {"user_id": refresh_data.user_id}

        # Create new token pair with rotation
        new_token_pair = self.create_token_pair(
            user_id=refresh_data.user_id,
            user_data=user_data,
            family_id=refresh_data.family_id,
            parent_token=refresh_token
        )

        return new_token_pair, False

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token

        Args:
            refresh_token: Refresh token to revoke

        Returns:
            True if revoked
        """
        token_hash = self.hash_token(refresh_token)
        refresh_data = self.token_store.get(token_hash)

        if refresh_data:
            refresh_data.is_revoked = True
            return True

        return False

    def _revoke_token_family(self, family_id: str) -> int:
        """
        Revoke all tokens in a family (on reuse detection)

        Args:
            family_id: Token family ID

        Returns:
            Number of tokens revoked
        """
        count = 0
        for token_data in self.token_store.values():
            if token_data.family_id == family_id:
                token_data.is_revoked = True
                count += 1
        return count

    def revoke_user_tokens(self, user_id: int) -> int:
        """
        Revoke all tokens for a user

        Args:
            user_id: User ID

        Returns:
            Number of tokens revoked
        """
        count = 0
        for token_data in self.token_store.values():
            if token_data.user_id == user_id:
                token_data.is_revoked = True
                count += 1
        return count

    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from store

        Returns:
            Number of tokens cleaned up
        """
        now = datetime.utcnow()
        expired_tokens = []

        for token_hash, token_data in self.token_store.items():
            expires = datetime.fromisoformat(token_data.expires_at)
            if now > expires:
                expired_tokens.append(token_hash)

        for token_hash in expired_tokens:
            del self.token_store[token_hash]

        return len(expired_tokens)


class TokenBlacklist:
    """Blacklist for revoked access tokens"""

    def __init__(self, redis_client):
        """
        Initialize token blacklist

        Args:
            redis_client: Redis client
        """
        self.redis = redis_client
        self.prefix = "blacklist:"

    def add_token(self, token: str, expires_in: int) -> None:
        """
        Add token to blacklist

        Args:
            token: JWT token
            expires_in: Seconds until token expires
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"{self.prefix}{token_hash}"
        self.redis.setex(key, expires_in, "1")

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted

        Args:
            token: JWT token

        Returns:
            True if blacklisted
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"{self.prefix}{token_hash}"
        return bool(self.redis.exists(key))


# Example usage
if __name__ == "__main__":
    from authentication.jwt_token_creation import JWTManager

    # Initialize managers
    jwt_manager = JWTManager()
    refresh_manager = RefreshTokenManager(jwt_manager)

    # Create initial token pair
    user_data = {"username": "john_doe", "role": "admin"}
    token_pair = refresh_manager.create_token_pair(123, user_data)

    print(f"Access Token: {token_pair.access_token[:50]}...")
    print(f"Refresh Token: {token_pair.refresh_token[:50]}...")
    print(f"Access expires: {token_pair.access_token_expires}")

    # Refresh access token
    result = refresh_manager.refresh_access_token(token_pair.refresh_token)
    if result:
        new_pair, reuse_detected = result
        print(f"\nNew Access Token: {new_pair.access_token[:50]}...")
        print(f"Reuse detected: {reuse_detected}")

    # Revoke user tokens
    revoked = refresh_manager.revoke_user_tokens(123)
    print(f"\nRevoked {revoked} tokens for user")
