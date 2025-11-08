"""Magic Link Authentication"""
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
import secrets
from urllib.parse import urlencode


class MagicLinkAuth:
    """Magic link authentication system"""

    def __init__(self, base_url: str, expiry_minutes: int = 15):
        self.base_url = base_url
        self.expiry_minutes = expiry_minutes
        self.tokens: Dict[str, Dict] = {}

    def generate_magic_link(self, email: str, redirect_url: str = "/") -> str:
        """Generate a magic link for email authentication"""
        try:
            token = secrets.token_urlsafe(32)
            self.tokens[token] = {
                'email': email,
                'redirect_url': redirect_url,
                'expires_at': datetime.now(timezone.utc) + timedelta(minutes=self.expiry_minutes)
            }

            params = urlencode({'token': token, 'email': email})
            return f"{self.base_url}/auth/verify?{params}"
        except Exception as e:
            raise Exception(f"Failed to generate magic link: {str(e)}")

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify magic link token"""
        try:
            if token not in self.tokens:
                return None

            data = self.tokens[token]
            if datetime.now(timezone.utc) > data['expires_at']:
                del self.tokens[token]
                return None

            # Return user data and clean up token
            del self.tokens[token]
            return {
                'email': data['email'],
                'redirect_url': data['redirect_url']
            }
        except Exception as e:
            raise Exception(f"Failed to verify token: {str(e)}")

    def revoke_token(self, token: str) -> bool:
        """Revoke a magic link token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
