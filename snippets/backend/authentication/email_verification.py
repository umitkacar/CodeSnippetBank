"""Email Verification Implementation"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import secrets


class EmailVerification:
    """Email verification system"""

    def __init__(self, expiry_hours: int = 24):
        self.expiry_hours = expiry_hours
        self.tokens: Dict[str, Dict] = {}

    def generate_verification_token(self, email: str) -> str:
        """Generate email verification token"""
        try:
            token = secrets.token_urlsafe(32)
            self.tokens[token] = {
                'email': email,
                'expires_at': datetime.now(timezone.utc) + timedelta(hours=self.expiry_hours)
            }
            return token
        except Exception as e:
            raise Exception(f"Failed to generate token: {str(e)}")

    def verify_email_token(self, token: str) -> Optional[str]:
        """Verify email token and return email if valid"""
        try:
            if token not in self.tokens:
                return None

            data = self.tokens[token]
            if datetime.now(timezone.utc) > data['expires_at']:
                del self.tokens[token]
                return None

            email = data['email']
            del self.tokens[token]
            return email
        except Exception as e:
            raise Exception(f"Failed to verify token: {str(e)}")
