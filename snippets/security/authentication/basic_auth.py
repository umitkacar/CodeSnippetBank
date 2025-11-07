"""
HTTP Basic Authentication
Production-ready Basic Auth implementation with rate limiting
"""
import base64
import secrets
from typing import Optional, Callable, Dict
from functools import wraps
import hashlib
import time


class BasicAuthHandler:
    """HTTP Basic Authentication handler"""

    def __init__(
        self,
        realm: str = "Protected Area",
        user_validator: Optional[Callable[[str, str], Optional[Dict]]] = None
    ):
        """
        Initialize Basic Auth handler

        Args:
            realm: Authentication realm
            user_validator: Function to validate credentials
        """
        self.realm = realm
        self.user_validator = user_validator or self._default_validator
        self.failed_attempts: Dict[str, list] = {}

    def _default_validator(self, username: str, password: str) -> Optional[Dict]:
        """Default validator (override in production)"""
        return None

    def parse_authorization_header(
        self,
        authorization: Optional[str]
    ) -> Optional[tuple[str, str]]:
        """
        Parse Basic Authorization header

        Args:
            authorization: Authorization header value

        Returns:
            Tuple of (username, password) or None
        """
        if not authorization:
            return None

        try:
            # Expected format: "Basic base64credentials"
            auth_type, credentials = authorization.split(' ', 1)

            if auth_type.lower() != 'basic':
                return None

            # Decode base64 credentials
            decoded = base64.b64decode(credentials).decode('utf-8')

            # Split username:password
            username, password = decoded.split(':', 1)

            return username, password

        except (ValueError, UnicodeDecodeError):
            return None

    def authenticate(
        self,
        authorization: Optional[str],
        client_ip: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Authenticate request

        Args:
            authorization: Authorization header value
            client_ip: Client IP for rate limiting

        Returns:
            User data if authenticated, None otherwise
        """
        # Parse credentials
        credentials = self.parse_authorization_header(authorization)

        if not credentials:
            return None

        username, password = credentials

        # Check rate limiting
        if client_ip and self._is_rate_limited(client_ip):
            return None

        # Validate credentials
        user = self.user_validator(username, password)

        if not user:
            # Record failed attempt
            if client_ip:
                self._record_failed_attempt(client_ip)
            return None

        # Clear failed attempts on success
        if client_ip and client_ip in self.failed_attempts:
            del self.failed_attempts[client_ip]

        return user

    def _is_rate_limited(self, client_ip: str) -> bool:
        """
        Check if IP is rate limited

        Args:
            client_ip: Client IP address

        Returns:
            True if rate limited
        """
        if client_ip not in self.failed_attempts:
            return False

        attempts = self.failed_attempts[client_ip]
        current_time = time.time()

        # Remove attempts older than 1 hour
        recent_attempts = [t for t in attempts if current_time - t < 3600]
        self.failed_attempts[client_ip] = recent_attempts

        # Rate limit: max 5 failed attempts per hour
        return len(recent_attempts) >= 5

    def _record_failed_attempt(self, client_ip: str) -> None:
        """Record failed authentication attempt"""
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = []

        self.failed_attempts[client_ip].append(time.time())

    def get_challenge_header(self) -> str:
        """
        Get WWW-Authenticate challenge header

        Returns:
            WWW-Authenticate header value
        """
        return f'Basic realm="{self.realm}", charset="UTF-8"'

    def require_auth(self, func):
        """
        Decorator to require basic authentication

        Usage:
            @auth.require_auth
            def protected_route(user):
                return f"Hello {user['username']}"
        """
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            client_ip = request.remote_addr

            user = self.authenticate(auth_header, client_ip)

            if not user:
                return {
                    'error': 'Unauthorized',
                    'www_authenticate': self.get_challenge_header()
                }, 401

            return func(user, *args, **kwargs)

        return wrapper


class DigestAuthHandler:
    """HTTP Digest Authentication (more secure than Basic)"""

    def __init__(
        self,
        realm: str = "Protected Area",
        secret_key: Optional[str] = None,
        nonce_timeout: int = 300
    ):
        """
        Initialize Digest Auth handler

        Args:
            realm: Authentication realm
            secret_key: Secret for nonce generation
            nonce_timeout: Nonce validity in seconds
        """
        self.realm = realm
        self.secret_key = secret_key or secrets.token_hex(32)
        self.nonce_timeout = nonce_timeout
        self.nonce_store: Dict[str, float] = {}

    def generate_nonce(self) -> str:
        """
        Generate nonce for Digest auth

        Returns:
            Nonce string
        """
        timestamp = int(time.time())
        random_data = secrets.token_hex(16)

        # Create nonce: timestamp:hash(timestamp:secret:random)
        nonce_data = f"{timestamp}:{self.secret_key}:{random_data}"
        nonce_hash = hashlib.md5(nonce_data.encode()).hexdigest()

        nonce = f"{timestamp}:{nonce_hash}"

        # Store nonce
        self.nonce_store[nonce] = time.time()

        return base64.b64encode(nonce.encode()).decode()

    def verify_nonce(self, nonce: str) -> bool:
        """
        Verify nonce validity

        Args:
            nonce: Nonce to verify

        Returns:
            True if valid
        """
        try:
            decoded = base64.b64decode(nonce).decode()
            timestamp_str, _ = decoded.split(':', 1)
            timestamp = int(timestamp_str)

            # Check if expired
            current_time = int(time.time())
            if current_time - timestamp > self.nonce_timeout:
                return False

            # Check if in store
            return decoded in self.nonce_store

        except (ValueError, UnicodeDecodeError):
            return False

    def calculate_ha1(
        self,
        username: str,
        password: str
    ) -> str:
        """
        Calculate HA1 for Digest auth

        Args:
            username: Username
            password: Password

        Returns:
            HA1 hash
        """
        ha1_data = f"{username}:{self.realm}:{password}"
        return hashlib.md5(ha1_data.encode()).hexdigest()

    def calculate_response(
        self,
        ha1: str,
        nonce: str,
        method: str,
        uri: str
    ) -> str:
        """
        Calculate expected response

        Args:
            ha1: HA1 hash
            nonce: Nonce
            method: HTTP method
            uri: Request URI

        Returns:
            Expected response hash
        """
        # HA2 = MD5(method:uri)
        ha2_data = f"{method}:{uri}"
        ha2 = hashlib.md5(ha2_data.encode()).hexdigest()

        # Response = MD5(HA1:nonce:HA2)
        response_data = f"{ha1}:{nonce}:{ha2}"
        return hashlib.md5(response_data.encode()).hexdigest()

    def get_challenge_header(self) -> str:
        """
        Get WWW-Authenticate Digest challenge

        Returns:
            WWW-Authenticate header value
        """
        nonce = self.generate_nonce()
        opaque = secrets.token_hex(16)

        return (
            f'Digest realm="{self.realm}", '
            f'qop="auth", '
            f'nonce="{nonce}", '
            f'opaque="{opaque}"'
        )


class APIKeyBasicAuth:
    """API Key authentication using Basic Auth format"""

    def __init__(self, api_key_validator: Callable[[str], Optional[Dict]]):
        """
        Initialize API Key Basic Auth

        Args:
            api_key_validator: Function to validate API key
        """
        self.api_key_validator = api_key_validator

    def authenticate(self, authorization: Optional[str]) -> Optional[Dict]:
        """
        Authenticate using API key as Basic Auth

        Format: Basic base64(api_key:)
        Username is API key, password is empty

        Args:
            authorization: Authorization header

        Returns:
            User/client data or None
        """
        if not authorization:
            return None

        try:
            auth_type, credentials = authorization.split(' ', 1)

            if auth_type.lower() != 'basic':
                return None

            decoded = base64.b64decode(credentials).decode('utf-8')

            # API key format: "api_key:" (empty password)
            if ':' in decoded:
                api_key, _ = decoded.split(':', 1)
            else:
                api_key = decoded

            return self.api_key_validator(api_key)

        except (ValueError, UnicodeDecodeError):
            return None


# Example usage
if __name__ == "__main__":
    # Create user validator
    def validate_user(username: str, password: str) -> Optional[Dict]:
        # In production, check against database
        users = {
            'admin': {
                'password': 'admin_pass',
                'user_id': 1,
                'username': 'admin',
                'role': 'admin'
            },
            'user': {
                'password': 'user_pass',
                'user_id': 2,
                'username': 'user',
                'role': 'user'
            }
        }

        user = users.get(username)
        if user and user['password'] == password:
            return {k: v for k, v in user.items() if k != 'password'}

        return None

    # Initialize Basic Auth
    auth = BasicAuthHandler(realm="My API", user_validator=validate_user)

    # Create Authorization header
    credentials = base64.b64encode(b"admin:admin_pass").decode()
    auth_header = f"Basic {credentials}"

    # Authenticate
    user = auth.authenticate(auth_header, client_ip="192.168.1.1")
    if user:
        print(f"Authenticated: {user}")
    else:
        print("Authentication failed")
        print(f"Challenge: {auth.get_challenge_header()}")

    # Test Digest Auth
    digest_auth = DigestAuthHandler()
    nonce = digest_auth.generate_nonce()
    print(f"\nDigest nonce: {nonce}")
    print(f"Challenge: {digest_auth.get_challenge_header()}")
