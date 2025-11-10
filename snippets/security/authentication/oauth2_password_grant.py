"""
OAuth2 Resource Owner Password Credentials Grant (DEPRECATED)
Note: Password grant is deprecated. Use Authorization Code flow instead.
Included for legacy support only.
"""
import secrets
from typing import Optional, Dict
import hashlib


class OAuth2PasswordGrant:
    """
    OAuth2 Password Grant (Deprecated)

    WARNING: This grant type is deprecated and should NOT be used.
    Use Authorization Code flow with PKCE instead.
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: Optional[str] = None
    ):
        """
        Initialize password grant client

        Args:
            token_url: Token endpoint
            client_id: Client ID
            client_secret: Optional client secret

        Warning:
            Password grant is deprecated. Do not use in new applications.
        """
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret

        print("⚠️  WARNING: Password grant is deprecated!")
        print("   Use Authorization Code flow with PKCE instead.")

    def get_token(
        self,
        username: str,
        password: str,
        scope: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get access token using username and password

        Args:
            username: User's username
            password: User's password
            scope: Optional scope

        Returns:
            Token response or None

        Warning:
            Exposes user credentials to client application.
            Use only for highly trusted first-party applications.
        """
        import requests

        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'client_id': self.client_id
        }

        if self.client_secret:
            data['client_secret'] = self.client_secret

        if scope:
            data['scope'] = scope

        try:
            response = requests.post(
                self.token_url,
                data=data,
                timeout=10
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Token request failed: {e}")
            return None


class OAuth2PasswordGrantServer:
    """Server-side password grant handling (Deprecated)"""

    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.clients: Dict[str, Dict] = {}

    def register_user(
        self,
        username: str,
        password: str,
        scopes: list[str]
    ) -> None:
        """
        Register user (for testing only)

        Args:
            username: Username
            password: Password (will be hashed)
            scopes: User's allowed scopes
        """
        # Hash password (use proper password hashing in production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        self.users[username] = {
            'password_hash': password_hash,
            'scopes': scopes
        }

    def register_client(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        allowed_grant_types: Optional[list] = None
    ) -> None:
        """
        Register OAuth2 client

        Args:
            client_id: Client ID
            client_secret: Optional client secret
            allowed_grant_types: List of allowed grant types
        """
        self.clients[client_id] = {
            'client_secret': client_secret,
            'allowed_grant_types': allowed_grant_types or ['password']
        }

    def issue_token(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: Optional[str] = None,
        scope: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Issue access token using password grant

        Args:
            username: Username
            password: Password
            client_id: Client ID
            client_secret: Client secret
            scope: Requested scope

        Returns:
            Token response or None
        """
        # Validate client
        client = self.clients.get(client_id)

        if not client:
            return {'error': 'invalid_client'}

        if 'password' not in client['allowed_grant_types']:
            return {'error': 'unauthorized_client'}

        if client['client_secret'] and client['client_secret'] != client_secret:
            return {'error': 'invalid_client'}

        # Validate user credentials
        user = self.users.get(username)

        if not user:
            return {'error': 'invalid_grant', 'error_description': 'Invalid credentials'}

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if password_hash != user['password_hash']:
            return {'error': 'invalid_grant', 'error_description': 'Invalid credentials'}

        # Validate scope
        if scope:
            requested_scopes = set(scope.split())
            allowed_scopes = set(user['scopes'])

            if not requested_scopes.issubset(allowed_scopes):
                return {'error': 'invalid_scope'}

            granted_scope = scope
        else:
            granted_scope = ' '.join(user['scopes'])

        # Generate tokens (use JWT in production)
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'scope': granted_scope
        }


class SecurePasswordGrantAlternative:
    """Secure alternatives to password grant"""

    @staticmethod
    def get_recommendation() -> str:
        """Get security recommendation"""
        return """
SECURITY RECOMMENDATION:
========================

The OAuth2 Password Grant is DEPRECATED and should NOT be used.

SECURITY ISSUES with Password Grant:
1. User credentials exposed to client application
2. No user consent flow
3. High risk if client is compromised
4. Credentials may be logged or stored
5. Cannot use MFA effectively
6. No way to revoke access without changing password

RECOMMENDED ALTERNATIVES:

1. Authorization Code Flow with PKCE (Best for most apps):
   ✓ User credentials never exposed to client
   ✓ Works with MFA
   ✓ Supports refresh tokens
   ✓ User consent flow
   ✓ Granular permission revocation

2. Client Credentials Grant (For machine-to-machine):
   ✓ No user credentials involved
   ✓ Service account authentication
   ✓ Suitable for backend services

3. Device Flow (For devices without browsers):
   ✓ User authorizes on separate device
   ✓ No typing of passwords on device
   ✓ Secure user authentication

WHEN Password Grant MIGHT be acceptable (rarely):
- First-party applications only (same organization)
- High trust environment
- Legacy system migration
- Better alternatives not available

Even then, consider these mitigations:
- Use with additional security layers
- Implement rate limiting
- Add anomaly detection
- Use short-lived tokens
- Require MFA

MIGRATION GUIDE:
If you must migrate from password grant:

1. For SPAs: Use Authorization Code + PKCE
2. For mobile apps: Use Authorization Code + PKCE
3. For backend services: Use Client Credentials
4. For IoT/TV: Use Device Flow
"""


# Example usage
if __name__ == "__main__":
    import os

    print(SecurePasswordGrantAlternative.get_recommendation())

    print("\n" + "="*60)
    print("Legacy Password Grant Example (DO NOT USE IN PRODUCTION)")
    print("="*60 + "\n")

    # Server setup
    server = OAuth2PasswordGrantServer()

    # Register client
    server.register_client(
        client_id="trusted_client",
        client_secret="client_secret_123",
        allowed_grant_types=["password", "refresh_token"]
    )

    # Register user (example only - use proper password hashing in production!)
    # Use environment variable: export TEST_USER_PASSWORD="your_password"
    server.register_user(
        username="john_doe",
        password=os.getenv("TEST_USER_PASSWORD", "changeme"),
        scopes=["read", "write"]
    )

    # Issue token
    # Use environment variables for credentials
    token_response = server.issue_token(
        username="john_doe",
        password=os.getenv("TEST_USER_PASSWORD", "changeme"),
        client_id="trusted_client",
        client_secret=os.getenv("OAUTH_CLIENT_SECRET", "changeme"),
        scope="read"
    )

    if 'access_token' in token_response:
        print("Token Response:")
        print(f"  Access Token: {token_response['access_token'][:50]}...")
        print(f"  Refresh Token: {token_response['refresh_token'][:50]}...")
        print(f"  Scope: {token_response['scope']}")
        print(f"  Expires in: {token_response['expires_in']} seconds")
    else:
        print(f"Error: {token_response.get('error')}")
        print(f"Description: {token_response.get('error_description')}")

    print("\n⚠️  REMEMBER: This is deprecated. Use Authorization Code + PKCE!")
