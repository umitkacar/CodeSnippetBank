"""
Cookie-Based Authentication
Production-ready secure cookie authentication with session management
"""
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from http.cookies import SimpleCookie
import json
import base64


class SecureCookieAuth:
    """Secure cookie-based authentication"""

    def __init__(
        self,
        secret_key: str,
        cookie_name: str = "session",
        max_age: int = 3600,
        domain: Optional[str] = None,
        path: str = "/",
        secure: bool = True,
        httponly: bool = True,
        samesite: str = "Lax"
    ):
        """
        Initialize secure cookie auth

        Args:
            secret_key: Secret key for signing cookies
            cookie_name: Name of the session cookie
            max_age: Cookie lifetime in seconds
            domain: Cookie domain
            path: Cookie path
            secure: Require HTTPS
            httponly: Prevent JavaScript access
            samesite: SameSite attribute (Strict/Lax/None)
        """
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.domain = domain
        self.path = path
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite

    def _sign_data(self, data: str) -> str:
        """
        Sign data with HMAC

        Args:
            data: Data to sign

        Returns:
            Signed data
        """
        signature = hmac.new(
            self.secret_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{data}.{signature}"

    def _verify_signature(self, signed_data: str) -> Optional[str]:
        """
        Verify signature and extract data

        Args:
            signed_data: Signed data string

        Returns:
            Original data if valid, None otherwise
        """
        try:
            data, signature = signed_data.rsplit('.', 1)

            expected_signature = hmac.new(
                self.secret_key,
                data.encode(),
                hashlib.sha256
            ).hexdigest()

            if secrets.compare_digest(signature, expected_signature):
                return data

        except (ValueError, AttributeError):
            pass

        return None

    def _encode_payload(self, payload: Dict) -> str:
        """
        Encode payload to base64 JSON

        Args:
            payload: Dictionary to encode

        Returns:
            Base64-encoded JSON string
        """
        json_str = json.dumps(payload, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return encoded

    def _decode_payload(self, encoded: str) -> Optional[Dict]:
        """
        Decode base64 JSON payload

        Args:
            encoded: Base64-encoded string

        Returns:
            Decoded dictionary or None
        """
        try:
            decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
            return json.loads(decoded)
        except (ValueError, json.JSONDecodeError):
            return None

    def create_cookie(self, user_id: int, user_data: Optional[Dict] = None) -> str:
        """
        Create signed session cookie

        Args:
            user_id: User identifier
            user_data: Additional user data

        Returns:
            Cookie value
        """
        payload = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.max_age)).isoformat(),
            'csrf_token': secrets.token_urlsafe(32),
            'data': user_data or {}
        }

        encoded = self._encode_payload(payload)
        signed = self._sign_data(encoded)

        return signed

    def verify_cookie(self, cookie_value: str) -> Optional[Dict]:
        """
        Verify and decode cookie

        Args:
            cookie_value: Cookie value to verify

        Returns:
            Decoded payload or None if invalid
        """
        # Verify signature
        encoded = self._verify_signature(cookie_value)

        if not encoded:
            return None

        # Decode payload
        payload = self._decode_payload(encoded)

        if not payload:
            return None

        # Check expiration
        try:
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.utcnow() > expires_at:
                return None
        except (KeyError, ValueError):
            return None

        return payload

    def get_cookie_header(self, cookie_value: str) -> str:
        """
        Get Set-Cookie header value

        Args:
            cookie_value: Cookie value

        Returns:
            Set-Cookie header string
        """
        cookie = SimpleCookie()
        cookie[self.cookie_name] = cookie_value
        cookie[self.cookie_name]['max-age'] = self.max_age
        cookie[self.cookie_name]['path'] = self.path

        if self.domain:
            cookie[self.cookie_name]['domain'] = self.domain

        if self.secure:
            cookie[self.cookie_name]['secure'] = True

        if self.httponly:
            cookie[self.cookie_name]['httponly'] = True

        cookie[self.cookie_name]['samesite'] = self.samesite

        return cookie[self.cookie_name].OutputString()

    def delete_cookie_header(self) -> str:
        """
        Get Set-Cookie header to delete cookie

        Returns:
            Set-Cookie header for deletion
        """
        cookie = SimpleCookie()
        cookie[self.cookie_name] = ""
        cookie[self.cookie_name]['max-age'] = 0
        cookie[self.cookie_name]['path'] = self.path
        cookie[self.cookie_name]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'

        return cookie[self.cookie_name].OutputString()


class RememberMeToken:
    """Remember Me token for persistent login"""

    def __init__(self, secret_key: str):
        """
        Initialize Remember Me handler

        Args:
            secret_key: Secret key for tokens
        """
        self.secret_key = secret_key.encode()

    def generate_token(
        self,
        user_id: int,
        series: Optional[str] = None
    ) -> tuple[str, str, str]:
        """
        Generate remember me token

        Args:
            user_id: User ID
            series: Token series (for rotation)

        Returns:
            Tuple of (series, token, token_hash)
        """
        if not series:
            series = secrets.token_urlsafe(32)

        token = secrets.token_urlsafe(32)

        # Hash token for storage
        token_hash = hashlib.sha256(
            f"{series}:{token}:{user_id}".encode()
        ).hexdigest()

        return series, token, token_hash

    def create_remember_cookie(
        self,
        user_id: int,
        series: Optional[str] = None
    ) -> tuple[str, str, str]:
        """
        Create remember me cookie

        Args:
            user_id: User ID
            series: Token series

        Returns:
            Tuple of (cookie_value, series, token_hash)
        """
        series, token, token_hash = self.generate_token(user_id, series)

        # Cookie format: user_id:series:token
        cookie_value = f"{user_id}:{series}:{token}"

        # Sign the cookie
        signature = hmac.new(
            self.secret_key,
            cookie_value.encode(),
            hashlib.sha256
        ).hexdigest()

        signed_cookie = f"{cookie_value}.{signature}"

        return signed_cookie, series, token_hash

    def verify_remember_cookie(
        self,
        cookie_value: str
    ) -> Optional[tuple[int, str, str]]:
        """
        Verify remember me cookie

        Args:
            cookie_value: Signed cookie value

        Returns:
            Tuple of (user_id, series, token) or None
        """
        try:
            # Split signature
            data, signature = cookie_value.rsplit('.', 1)

            # Verify signature
            expected_sig = hmac.new(
                self.secret_key,
                data.encode(),
                hashlib.sha256
            ).hexdigest()

            if not secrets.compare_digest(signature, expected_sig):
                return None

            # Parse cookie
            user_id, series, token = data.split(':', 2)

            return int(user_id), series, token

        except (ValueError, AttributeError):
            return None


class CSRFProtection:
    """CSRF token protection"""

    def __init__(self, secret_key: str):
        """
        Initialize CSRF protection

        Args:
            secret_key: Secret key for token generation
        """
        self.secret_key = secret_key.encode()

    def generate_token(self, session_token: str) -> str:
        """
        Generate CSRF token for session

        Args:
            session_token: Session identifier

        Returns:
            CSRF token
        """
        # Generate random token
        random_part = secrets.token_urlsafe(32)

        # Sign with session token
        signature = hmac.new(
            self.secret_key,
            f"{session_token}:{random_part}".encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{random_part}.{signature}"

    def verify_token(
        self,
        csrf_token: str,
        session_token: str
    ) -> bool:
        """
        Verify CSRF token

        Args:
            csrf_token: CSRF token from request
            session_token: Session identifier

        Returns:
            True if valid
        """
        try:
            random_part, signature = csrf_token.rsplit('.', 1)

            expected_sig = hmac.new(
                self.secret_key,
                f"{session_token}:{random_part}".encode(),
                hashlib.sha256
            ).hexdigest()

            return secrets.compare_digest(signature, expected_sig)

        except (ValueError, AttributeError):
            return False


# Example usage
if __name__ == "__main__":
    # Initialize cookie auth
    secret_key = secrets.token_urlsafe(32)
    cookie_auth = SecureCookieAuth(secret_key)

    # Create session cookie
    user_id = 123
    cookie_value = cookie_auth.create_cookie(
        user_id,
        user_data={'username': 'john_doe', 'role': 'admin'}
    )

    print(f"Cookie value: {cookie_value[:50]}...")

    # Get Set-Cookie header
    set_cookie = cookie_auth.get_cookie_header(cookie_value)
    print(f"Set-Cookie: {set_cookie}")

    # Verify cookie
    payload = cookie_auth.verify_cookie(cookie_value)
    if payload:
        print(f"User ID: {payload['user_id']}")
        print(f"User data: {payload['data']}")
        print(f"CSRF token: {payload['csrf_token']}")

    # Remember Me example
    remember_me = RememberMeToken(secret_key)
    remember_cookie, series, token_hash = remember_me.create_remember_cookie(user_id)
    print(f"\nRemember me cookie: {remember_cookie[:50]}...")
    print(f"Series: {series}")
    print(f"Token hash: {token_hash}")

    # CSRF protection
    csrf = CSRFProtection(secret_key)
    csrf_token = csrf.generate_token(cookie_value)
    print(f"\nCSRF token: {csrf_token[:50]}...")

    is_valid = csrf.verify_token(csrf_token, cookie_value)
    print(f"CSRF token valid: {is_valid}")
