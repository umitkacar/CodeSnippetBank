"""
JWT Token Creation and Validation
Production-ready JWT implementation with security best practices
"""
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import secrets


class JWTManager:
    """Secure JWT token manager with proper error handling"""

    def __init__(self, secret_key: Optional[str] = None, algorithm: str = 'HS256'):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data: Payload data to encode
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a long-lived refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)


# Example usage
if __name__ == "__main__":
    jwt_manager = JWTManager()

    # Create access token
    user_data = {"user_id": 123, "username": "john_doe", "role": "admin"}
    access_token = jwt_manager.create_access_token(user_data)
    print(f"Access Token: {access_token}")

    # Verify token
    payload = jwt_manager.verify_token(access_token)
    if payload:
        print(f"Verified Payload: {payload}")

    # Create refresh token
    refresh_token = jwt_manager.create_refresh_token({"user_id": 123})
    print(f"Refresh Token: {refresh_token}")
