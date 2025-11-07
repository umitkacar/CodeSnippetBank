"""
OAuth2 Client Credentials Flow
Production-ready machine-to-machine authentication
"""
import requests
import secrets
import hashlib
import time
from typing import Optional, Dict
from datetime import datetime, timedelta


class OAuth2ClientCredentials:
    """OAuth2 Client Credentials Flow for M2M authentication"""

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: Optional[str] = None
    ):
        """
        Initialize OAuth2 Client Credentials

        Args:
            token_url: Token endpoint URL
            client_id: Client ID
            client_secret: Client secret
            scope: Optional scope
        """
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self._cached_token: Optional[Dict] = None

    def get_access_token(self, use_cache: bool = True) -> Optional[str]:
        """
        Get access token using client credentials

        Args:
            use_cache: Use cached token if valid

        Returns:
            Access token or None
        """
        # Check cache
        if use_cache and self._cached_token:
            if not self._is_token_expired(self._cached_token):
                return self._cached_token['access_token']

        # Request new token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        if self.scope:
            data['scope'] = self.scope

        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )

            response.raise_for_status()
            token_data = response.json()

            # Add expiration timestamp
            token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)

            # Cache token
            self._cached_token = token_data

            return token_data['access_token']

        except requests.exceptions.RequestException as e:
            print(f"Token request failed: {e}")
            return None

    def _is_token_expired(self, token_data: Dict) -> bool:
        """
        Check if token is expired

        Args:
            token_data: Token response data

        Returns:
            True if expired
        """
        expires_at = token_data.get('expires_at', 0)
        # Consider token expired 60s before actual expiration
        return time.time() >= (expires_at - 60)

    def make_authenticated_request(
        self,
        url: str,
        method: str = 'GET',
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Make authenticated API request

        Args:
            url: API endpoint URL
            method: HTTP method
            **kwargs: Additional requests arguments

        Returns:
            Response object or None
        """
        token = self.get_access_token()

        if not token:
            return None

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers

        try:
            response = requests.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


class ClientCredentialsManager:
    """Manage client credentials with hashing"""

    def __init__(self, secret_pepper: str):
        """
        Initialize credentials manager

        Args:
            secret_pepper: Secret pepper for hashing
        """
        self.pepper = secret_pepper

    def generate_credentials(self) -> tuple[str, str]:
        """
        Generate new client credentials

        Returns:
            Tuple of (client_id, client_secret)
        """
        client_id = f"client_{secrets.token_urlsafe(16)}"
        client_secret = secrets.token_urlsafe(48)

        return client_id, client_secret

    def hash_client_secret(self, client_secret: str) -> str:
        """
        Hash client secret for storage

        Args:
            client_secret: Plain client secret

        Returns:
            Hashed secret
        """
        import hmac

        hashed = hmac.new(
            self.pepper.encode(),
            client_secret.encode(),
            hashlib.sha256
        ).hexdigest()

        return hashed

    def verify_client_secret(
        self,
        client_secret: str,
        hashed_secret: str
    ) -> bool:
        """
        Verify client secret

        Args:
            client_secret: Plain secret to verify
            hashed_secret: Stored hash

        Returns:
            True if valid
        """
        expected_hash = self.hash_client_secret(client_secret)
        return secrets.compare_digest(expected_hash, hashed_secret)


class OAuth2ClientCredentialsServer:
    """OAuth2 server implementation for client credentials"""

    def __init__(self, credentials_manager: ClientCredentialsManager):
        """
        Initialize OAuth2 server

        Args:
            credentials_manager: Credentials manager
        """
        self.credentials_manager = credentials_manager
        self.clients: Dict[str, Dict] = {}

    def register_client(
        self,
        name: str,
        scopes: list[str]
    ) -> tuple[str, str]:
        """
        Register new OAuth2 client

        Args:
            name: Client name
            scopes: Allowed scopes

        Returns:
            Tuple of (client_id, client_secret)
        """
        client_id, client_secret = self.credentials_manager.generate_credentials()
        secret_hash = self.credentials_manager.hash_client_secret(client_secret)

        self.clients[client_id] = {
            'name': name,
            'secret_hash': secret_hash,
            'scopes': scopes,
            'created_at': datetime.utcnow().isoformat()
        }

        return client_id, client_secret

    def verify_client(
        self,
        client_id: str,
        client_secret: str
    ) -> Optional[Dict]:
        """
        Verify client credentials

        Args:
            client_id: Client ID
            client_secret: Client secret

        Returns:
            Client data if valid, None otherwise
        """
        client = self.clients.get(client_id)

        if not client:
            return None

        if not self.credentials_manager.verify_client_secret(
            client_secret,
            client['secret_hash']
        ):
            return None

        return client

    def issue_access_token(
        self,
        client_id: str,
        client_secret: str,
        requested_scope: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Issue access token for client credentials

        Args:
            client_id: Client ID
            client_secret: Client secret
            requested_scope: Requested scope

        Returns:
            Token response or None
        """
        # Verify client
        client = self.verify_client(client_id, client_secret)

        if not client:
            return None

        # Validate scope
        if requested_scope:
            requested_scopes = set(requested_scope.split())
            allowed_scopes = set(client['scopes'])

            if not requested_scopes.issubset(allowed_scopes):
                return None

            granted_scope = requested_scope
        else:
            granted_scope = ' '.join(client['scopes'])

        # Generate access token (in production, use JWT)
        from authentication.jwt_token_creation import JWTManager

        jwt_manager = JWTManager()

        token_data = {
            'client_id': client_id,
            'scope': granted_scope,
            'token_type': 'client_credentials'
        }

        access_token = jwt_manager.create_access_token(
            token_data,
            expires_delta=timedelta(hours=1)
        )

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': granted_scope
        }


# Example usage
if __name__ == "__main__":
    # Client side example
    oauth_client = OAuth2ClientCredentials(
        token_url="https://auth.example.com/oauth/token",
        client_id="your_client_id",
        client_secret="your_client_secret",
        scope="api.read api.write"
    )

    # Get access token
    token = oauth_client.get_access_token()
    if token:
        print(f"Access token: {token[:50]}...")

        # Make authenticated request
        response = oauth_client.make_authenticated_request(
            "https://api.example.com/data",
            method="GET"
        )

        if response:
            print(f"API Response: {response.status_code}")

    # Server side example
    pepper = secrets.token_hex(32)
    creds_manager = ClientCredentialsManager(pepper)
    oauth_server = OAuth2ClientCredentialsServer(creds_manager)

    # Register a client
    client_id, client_secret = oauth_server.register_client(
        name="My Application",
        scopes=["api.read", "api.write"]
    )

    print(f"\nRegistered Client:")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret}")

    # Issue token
    token_response = oauth_server.issue_access_token(
        client_id,
        client_secret,
        requested_scope="api.read"
    )

    if token_response:
        print(f"\nToken Response:")
        print(f"Access Token: {token_response['access_token'][:50]}...")
        print(f"Scope: {token_response['scope']}")
        print(f"Expires in: {token_response['expires_in']}s")
