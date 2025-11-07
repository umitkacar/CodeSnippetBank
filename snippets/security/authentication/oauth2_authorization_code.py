"""
OAuth2 Authorization Code Flow Implementation
Production-ready OAuth2 with PKCE support
"""
import secrets
import hashlib
import base64
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
import requests


class OAuth2Client:
    """OAuth2 client with Authorization Code Flow and PKCE"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        redirect_uri: str,
        scope: Optional[str] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scope = scope or "openid profile email"

    def generate_pkce_pair(self) -> Tuple[str, str]:
        """
        Generate PKCE code verifier and challenge

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')

        # Generate code challenge (SHA256 hash of verifier)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')

        return code_verifier, code_challenge

    def get_authorization_url(
        self,
        state: Optional[str] = None,
        use_pkce: bool = True
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate authorization URL

        Args:
            state: Optional state parameter for CSRF protection
            use_pkce: Whether to use PKCE

        Returns:
            Tuple of (authorization_url, session_data)
        """
        state = state or secrets.token_urlsafe(32)
        session_data = {"state": state}

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state
        }

        if use_pkce:
            code_verifier, code_challenge = self.generate_pkce_pair()
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
            session_data["code_verifier"] = code_verifier

        auth_url = f"{self.authorization_url}?{urlencode(params)}"
        return auth_url, session_data

    def exchange_code_for_token(
        self,
        code: str,
        code_verifier: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback
            code_verifier: PKCE code verifier if used

        Returns:
            Token response dictionary
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        if code_verifier:
            data["code_verifier"] = code_verifier

        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Token exchange failed: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            New token response
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(
                self.token_url,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Token refresh failed: {e}")
            return None

    def revoke_token(self, token: str, token_type_hint: str = "access_token") -> bool:
        """
        Revoke access or refresh token

        Args:
            token: Token to revoke
            token_type_hint: Type of token (access_token or refresh_token)

        Returns:
            True if successful
        """
        revocation_url = self.token_url.replace("/token", "/revoke")

        data = {
            "token": token,
            "token_type_hint": token_type_hint,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(revocation_url, data=data, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


# Example usage
if __name__ == "__main__":
    oauth_client = OAuth2Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
        authorization_url="https://provider.com/oauth/authorize",
        token_url="https://provider.com/oauth/token",
        redirect_uri="https://yourapp.com/callback"
    )

    # Step 1: Get authorization URL
    auth_url, session = oauth_client.get_authorization_url(use_pkce=True)
    print(f"Authorization URL: {auth_url}")
    print(f"Session data: {session}")

    # Step 2: User authorizes and you receive callback with code
    # code = "authorization_code_from_callback"
    # tokens = oauth_client.exchange_code_for_token(
    #     code,
    #     code_verifier=session.get("code_verifier")
    # )
