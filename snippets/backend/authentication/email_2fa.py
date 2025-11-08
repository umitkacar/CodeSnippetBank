"""Email-based 2FA Implementation"""
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
import secrets
import string


class EmailTwoFactorAuth:
    """Email-based two-factor authentication"""

    def __init__(self, code_length: int = 6, expiry_minutes: int = 10):
        self.code_length = code_length
        self.expiry_minutes = expiry_minutes
        self.codes: Dict[str, Dict] = {}

    def generate_code(self, email: str) -> str:
        """Generate a verification code for email"""
        try:
            code = ''.join(secrets.choice(string.digits) for _ in range(self.code_length))
            self.codes[email] = {
                'code': code,
                'expires_at': datetime.now(timezone.utc) + timedelta(minutes=self.expiry_minutes)
            }
            return code
        except Exception as e:
            raise Exception(f"Failed to generate code: {str(e)}")

    def verify_code(self, email: str, code: str) -> bool:
        """Verify the email code"""
        try:
            if email not in self.codes:
                return False

            stored = self.codes[email]
            if datetime.now(timezone.utc) > stored['expires_at']:
                del self.codes[email]
                return False

            if stored['code'] == code:
                del self.codes[email]
                return True

            return False
        except Exception as e:
            raise Exception(f"Failed to verify code: {str(e)}")

    def is_code_valid(self, email: str) -> bool:
        """Check if a valid code exists for email"""
        if email not in self.codes:
            return False
        return datetime.now(timezone.utc) < self.codes[email]['expires_at']
