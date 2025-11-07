"""
OAuth2 Implicit Flow (Legacy)
Note: Implicit flow is deprecated. Use Authorization Code with PKCE instead.
Included for legacy support only.
"""
import secrets
from urllib.parse import urlencode, parse_qs
from typing import Optional, Dict
from datetime import datetime, timedelta


class OAuth2ImplicitFlow:
    """OAuth2 Implicit Flow (Deprecated - Use Authorization Code + PKCE)"""

    def __init__(
        self,
        authorization_url: str,
        client_id: str,
        redirect_uri: str,
        scope: Optional[str] = None
    ):
        """
        Initialize OAuth2 Implicit Flow

        Args:
            authorization_url: Authorization endpoint
            client_id: Client ID
            redirect_uri: Redirect URI
            scope: Optional scope

        Warning:
            Implicit flow is deprecated and insecure.
            Use Authorization Code flow with PKCE instead.
        """
        self.authorization_url = authorization_url
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope or "openid profile email"

        print("⚠️  WARNING: Implicit flow is deprecated and insecure!")
        print("   Please use Authorization Code flow with PKCE instead.")

    def get_authorization_url(
        self,
        state: Optional[str] = None,
        nonce: Optional[str] = None
    ) -> tuple[str, Dict]:
        """
        Get authorization URL for implicit flow

        Args:
            state: State parameter for CSRF protection
            nonce: Nonce for ID token validation

        Returns:
            Tuple of (authorization_url, session_data)
        """
        state = state or secrets.token_urlsafe(32)
        nonce = nonce or secrets.token_urlsafe(32)

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'token',  # or 'id_token token' for OpenID
            'scope': self.scope,
            'state': state,
            'nonce': nonce
        }

        auth_url = f"{self.authorization_url}?{urlencode(params)}"

        session_data = {
            'state': state,
            'nonce': nonce
        }

        return auth_url, session_data

    def parse_redirect_response(
        self,
        fragment: str,
        expected_state: str
    ) -> Optional[Dict]:
        """
        Parse tokens from redirect URL fragment

        Args:
            fragment: URL fragment (after #)
            expected_state: Expected state value

        Returns:
            Token data or None if invalid
        """
        # Parse fragment
        params = parse_qs(fragment)

        # Extract values (parse_qs returns lists)
        access_token = params.get('access_token', [None])[0]
        token_type = params.get('token_type', [None])[0]
        expires_in = params.get('expires_in', [None])[0]
        state = params.get('state', [None])[0]
        id_token = params.get('id_token', [None])[0]

        # Validate state
        if not state or state != expected_state:
            print("State mismatch - possible CSRF attack")
            return None

        if not access_token:
            error = params.get('error', [None])[0]
            error_description = params.get('error_description', [''])[0]
            print(f"Authorization error: {error} - {error_description}")
            return None

        return {
            'access_token': access_token,
            'token_type': token_type or 'Bearer',
            'expires_in': int(expires_in) if expires_in else 3600,
            'id_token': id_token
        }


class OAuth2ImplicitServer:
    """Server-side implicit flow handling (Legacy)"""

    def __init__(self):
        self.clients: Dict[str, Dict] = {}

    def register_client(
        self,
        client_id: str,
        redirect_uris: list[str],
        allowed_scopes: list[str]
    ) -> None:
        """
        Register OAuth2 client for implicit flow

        Args:
            client_id: Client ID
            redirect_uris: List of allowed redirect URIs
            allowed_scopes: List of allowed scopes
        """
        self.clients[client_id] = {
            'redirect_uris': redirect_uris,
            'allowed_scopes': allowed_scopes
        }

    def authorize_request(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        state: str,
        nonce: str
    ) -> Optional[str]:
        """
        Process authorization request

        Args:
            client_id: Client ID
            redirect_uri: Redirect URI
            scope: Requested scope
            state: State parameter
            nonce: Nonce parameter

        Returns:
            Redirect URL with token in fragment
        """
        # Validate client
        client = self.clients.get(client_id)

        if not client:
            return None

        # Validate redirect URI
        if redirect_uri not in client['redirect_uris']:
            return None

        # Validate scope
        requested_scopes = set(scope.split())
        allowed_scopes = set(client['allowed_scopes'])

        if not requested_scopes.issubset(allowed_scopes):
            return None

        # In production, show authorization page to user
        # For this example, we'll auto-approve

        # Generate access token (in production, use JWT)
        access_token = secrets.token_urlsafe(32)

        # Build redirect URL with token in fragment
        fragment_params = {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': '3600',
            'state': state,
            'scope': scope
        }

        redirect_url = f"{redirect_uri}#{urlencode(fragment_params)}"

        return redirect_url


class SecureImplicitAlternative:
    """
    Secure alternative to implicit flow using Authorization Code + PKCE
    """

    @staticmethod
    def get_recommendation() -> str:
        """Get security recommendation"""
        return """
SECURITY RECOMMENDATION:
========================

The OAuth2 Implicit Flow is DEPRECATED and should NOT be used for new applications.

SECURITY ISSUES with Implicit Flow:
1. Access tokens exposed in URL (browser history, logs)
2. No client authentication
3. No refresh tokens
4. Vulnerable to token theft
5. Cannot use PKCE effectively

RECOMMENDED ALTERNATIVE:
Use Authorization Code Flow with PKCE for single-page applications (SPAs).

Benefits of Authorization Code + PKCE:
✓ Tokens not exposed in URL
✓ PKCE provides proof of possession
✓ Supports refresh tokens
✓ Better security for public clients
✓ Current best practice for SPAs

Example:
    from authentication.oauth2_authorization_code import OAuth2Client

    oauth_client = OAuth2Client(
        client_id="your_client_id",
        client_secret="",  # Empty for public clients
        authorization_url="https://provider.com/oauth/authorize",
        token_url="https://provider.com/oauth/token",
        redirect_uri="https://yourapp.com/callback"
    )

    # Get authorization URL with PKCE
    auth_url, session = oauth_client.get_authorization_url(use_pkce=True)
"""


# Example usage
if __name__ == "__main__":
    print(SecureImplicitAlternative.get_recommendation())

    print("\n" + "="*60)
    print("Legacy Implicit Flow Example (DO NOT USE IN PRODUCTION)")
    print("="*60 + "\n")

    # Client side
    implicit_client = OAuth2ImplicitFlow(
        authorization_url="https://oauth.example.com/authorize",
        client_id="your_client_id",
        redirect_uri="https://yourapp.com/callback"
    )

    # Get authorization URL
    auth_url, session = implicit_client.get_authorization_url()

    print(f"Authorization URL: {auth_url}")
    print(f"Session data: {session}")

    # Server side
    server = OAuth2ImplicitServer()

    # Register client
    server.register_client(
        client_id="your_client_id",
        redirect_uris=["https://yourapp.com/callback"],
        allowed_scopes=["read", "write", "profile"]
    )

    # Process authorization
    redirect_url = server.authorize_request(
        client_id="your_client_id",
        redirect_uri="https://yourapp.com/callback",
        scope="read profile",
        state=session['state'],
        nonce=session['nonce']
    )

    if redirect_url:
        print(f"\nRedirect URL: {redirect_url[:100]}...")

        # Parse response
        fragment = redirect_url.split('#')[1]
        tokens = implicit_client.parse_redirect_response(
            fragment,
            session['state']
        )

        if tokens:
            print(f"\nAccess Token: {tokens['access_token'][:50]}...")
            print(f"Expires in: {tokens['expires_in']} seconds")

    print("\n⚠️  REMEMBER: Use Authorization Code + PKCE instead!")
