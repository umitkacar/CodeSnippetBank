"""
Secure Session Management
Production-ready session handling with Redis backend
"""
import secrets
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis


class SessionManager:
    """Secure session management with Redis"""

    def __init__(
        self,
        redis_client: redis.Redis,
        session_lifetime: int = 3600,  # 1 hour
        session_prefix: str = "session:"
    ):
        """
        Initialize session manager

        Args:
            redis_client: Redis client instance
            session_lifetime: Session lifetime in seconds
            session_prefix: Prefix for Redis keys
        """
        self.redis = redis_client
        self.session_lifetime = session_lifetime
        self.session_prefix = session_prefix

    def generate_session_id(self) -> str:
        """
        Generate cryptographically secure session ID

        Returns:
            Session ID string
        """
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)

        # Hash with SHA256 for consistency
        session_id = hashlib.sha256(random_bytes).hexdigest()

        return session_id

    def create_session(self, user_id: int, data: Optional[Dict] = None) -> str:
        """
        Create a new session

        Args:
            user_id: User ID
            data: Additional session data

        Returns:
            Session ID
        """
        session_id = self.generate_session_id()
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "data": data or {}
        }

        # Store in Redis with expiration
        key = f"{self.session_prefix}{session_id}"
        self.redis.setex(
            key,
            self.session_lifetime,
            json.dumps(session_data)
        )

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        key = f"{self.session_prefix}{session_id}"
        data = self.redis.get(key)

        if data:
            session_data = json.loads(data)

            # Update last activity
            session_data["last_activity"] = datetime.utcnow().isoformat()
            self.redis.setex(
                key,
                self.session_lifetime,
                json.dumps(session_data)
            )

            return session_data

        return None

    def update_session(
        self,
        session_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Update session data

        Args:
            session_id: Session ID
            data: Data to update

        Returns:
            True if successful
        """
        session_data = self.get_session(session_id)

        if session_data:
            session_data["data"].update(data)
            session_data["last_activity"] = datetime.utcnow().isoformat()

            key = f"{self.session_prefix}{session_id}"
            self.redis.setex(
                key,
                self.session_lifetime,
                json.dumps(session_data)
            )
            return True

        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session (logout)

        Args:
            session_id: Session ID

        Returns:
            True if deleted
        """
        key = f"{self.session_prefix}{session_id}"
        return bool(self.redis.delete(key))

    def delete_user_sessions(self, user_id: int) -> int:
        """
        Delete all sessions for a user

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        pattern = f"{self.session_prefix}*"
        deleted = 0

        for key in self.redis.scan_iter(match=pattern):
            data = self.redis.get(key)
            if data:
                session_data = json.loads(data)
                if session_data.get("user_id") == user_id:
                    self.redis.delete(key)
                    deleted += 1

        return deleted

    def validate_session(self, session_id: str) -> bool:
        """
        Check if session is valid

        Args:
            session_id: Session ID

        Returns:
            True if session exists and is valid
        """
        return self.get_session(session_id) is not None

    def get_session_count(self, user_id: int) -> int:
        """
        Count active sessions for a user

        Args:
            user_id: User ID

        Returns:
            Number of active sessions
        """
        pattern = f"{self.session_prefix}*"
        count = 0

        for key in self.redis.scan_iter(match=pattern):
            data = self.redis.get(key)
            if data:
                session_data = json.loads(data)
                if session_data.get("user_id") == user_id:
                    count += 1

        return count


class SecureCookieSession:
    """Secure cookie-based session helper"""

    @staticmethod
    def get_secure_cookie_options(
        max_age: int = 3600,
        domain: Optional[str] = None,
        path: str = "/"
    ) -> Dict[str, Any]:
        """
        Get secure cookie options

        Args:
            max_age: Cookie lifetime in seconds
            domain: Cookie domain
            path: Cookie path

        Returns:
            Cookie options dictionary
        """
        options = {
            "max_age": max_age,
            "path": path,
            "secure": True,  # HTTPS only
            "httponly": True,  # Not accessible via JavaScript
            "samesite": "Lax"  # CSRF protection
        }

        if domain:
            options["domain"] = domain

        return options

    @staticmethod
    def sign_cookie_value(value: str, secret: str) -> str:
        """
        Sign cookie value for integrity

        Args:
            value: Cookie value
            secret: Secret key

        Returns:
            Signed value
        """
        signature = hmac.new(
            secret.encode(),
            value.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{value}.{signature}"

    @staticmethod
    def verify_cookie_signature(
        signed_value: str,
        secret: str
    ) -> Optional[str]:
        """
        Verify and extract cookie value

        Args:
            signed_value: Signed cookie value
            secret: Secret key

        Returns:
            Original value if valid, None otherwise
        """
        try:
            value, signature = signed_value.rsplit(".", 1)

            expected_signature = hmac.new(
                secret.encode(),
                value.encode(),
                hashlib.sha256
            ).hexdigest()

            if secrets.compare_digest(signature, expected_signature):
                return value

        except ValueError:
            pass

        return None


# Example usage
if __name__ == "__main__":
    # Initialize Redis client
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=False
    )

    # Create session manager
    session_mgr = SessionManager(redis_client)

    # Create a new session
    user_id = 123
    session_id = session_mgr.create_session(
        user_id,
        data={"role": "admin", "ip": "192.168.1.1"}
    )
    print(f"Created session: {session_id}")

    # Retrieve session
    session = session_mgr.get_session(session_id)
    print(f"Session data: {session}")

    # Update session
    session_mgr.update_session(session_id, {"last_page": "/dashboard"})

    # Validate session
    is_valid = session_mgr.validate_session(session_id)
    print(f"Session valid: {is_valid}")

    # Get secure cookie options
    cookie_options = SecureCookieSession.get_secure_cookie_options()
    print(f"Cookie options: {cookie_options}")

    # Delete session
    session_mgr.delete_session(session_id)
    print(f"Session deleted")
