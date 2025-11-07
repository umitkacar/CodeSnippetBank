"""
OAuth2 Token Introspection (RFC 7662)
Production-ready token introspection endpoint
"""
import secrets
import time
from typing import Optional, Dict, Set
from datetime import datetime
import jwt


class TokenIntrospectionEndpoint:
    """OAuth2 Token Introspection Implementation"""

    def __init__(self, jwt_secret: str):
        """
        Initialize token introspection endpoint

        Args:
            jwt_secret: Secret for JWT validation
        """
        self.jwt_secret = jwt_secret
        self.revoked_tokens: Set[str] = set()

    def introspect_token(
        self,
        token: str,
        token_type_hint: Optional[str] = None
    ) -> Dict:
        """
        Introspect token and return metadata

        Args:
            token: Token to introspect
            token_type_hint: Hint about token type (access_token, refresh_token)

        Returns:
            Token introspection response (RFC 7662)
        """
        # Check if token is revoked
        if self._is_revoked(token):
            return {'active': False}

        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256']
            )

            # Check expiration
            exp = payload.get('exp')
            if exp and time.time() > exp:
                return {'active': False}

            # Return token metadata
            return {
                'active': True,
                'scope': payload.get('scope', ''),
                'client_id': payload.get('client_id', payload.get('aud')),
                'username': payload.get('username', payload.get('sub')),
                'token_type': token_type_hint or 'Bearer',
                'exp': payload.get('exp'),
                'iat': payload.get('iat'),
                'nbf': payload.get('nbf'),
                'sub': payload.get('sub'),
                'aud': payload.get('aud'),
                'iss': payload.get('iss'),
                'jti': payload.get('jti')
            }

        except jwt.ExpiredSignatureError:
            return {'active': False}

        except jwt.InvalidTokenError:
            return {'active': False}

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token

        Args:
            token: Token to revoke

        Returns:
            True if revoked
        """
        self.revoked_tokens.add(token)
        return True

    def _is_revoked(self, token: str) -> bool:
        """Check if token is revoked"""
        return token in self.revoked_tokens


class TokenRevocationEndpoint:
    """OAuth2 Token Revocation (RFC 7009)"""

    def __init__(self, introspection_endpoint: TokenIntrospectionEndpoint):
        """
        Initialize revocation endpoint

        Args:
            introspection_endpoint: Token introspection endpoint
        """
        self.introspection = introspection_endpoint

    def revoke_token(
        self,
        token: str,
        token_type_hint: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> bool:
        """
        Revoke token (RFC 7009)

        Args:
            token: Token to revoke
            token_type_hint: Hint about token type
            client_id: Client ID (for authentication)

        Returns:
            True if successful
        """
        # Validate token belongs to client (in production)
        # if client_id:
        #     introspection = self.introspection.introspect_token(token)
        #     if introspection.get('client_id') != client_id:
        #         return False

        return self.introspection.revoke_token(token)


# Example usage
if __name__ == "__main__":
    # Create introspection endpoint
    secret = secrets.token_urlsafe(32)
    introspection_ep = TokenIntrospectionEndpoint(secret)

    # Create a sample JWT token
    payload = {
        'sub': 'user_123',
        'username': 'john_doe',
        'client_id': 'client_abc',
        'scope': 'read write',
        'exp': int(time.time()) + 3600,
        'iat': int(time.time()),
        'jti': secrets.token_urlsafe(16)
    }

    token = jwt.encode(payload, secret, algorithm='HS256')
    print(f"Token: {token[:50]}...")

    # Introspect token
    result = introspection_ep.introspect_token(token)
    print(f"\nIntrospection result:")
    print(f"  Active: {result['active']}")

    if result['active']:
        print(f"  Username: {result.get('username')}")
        print(f"  Client ID: {result.get('client_id')}")
        print(f"  Scope: {result.get('scope')}")
        print(f"  Expires: {datetime.fromtimestamp(result['exp']).isoformat()}")

    # Revoke token
    revocation_ep = TokenRevocationEndpoint(introspection_ep)
    revoked = revocation_ep.revoke_token(token)
    print(f"\nToken revoked: {revoked}")

    # Introspect again
    result = introspection_ep.introspect_token(token)
    print(f"Active after revocation: {result['active']}")
