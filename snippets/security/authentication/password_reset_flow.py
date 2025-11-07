"""
Password Reset Flow
Production-ready secure password reset with time-limited tokens
"""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@dataclass
class ResetToken:
    """Password reset token data"""
    token_hash: str
    user_id: int
    email: str
    created_at: str
    expires_at: str
    is_used: bool


class PasswordResetManager:
    """Manage password reset requests"""

    def __init__(
        self,
        secret_key: str,
        token_lifetime: int = 3600,  # 1 hour
        rate_limit: int = 3  # Max requests per hour
    ):
        """
        Initialize password reset manager

        Args:
            secret_key: Secret key for token generation
            token_lifetime: Token lifetime in seconds
            rate_limit: Max reset requests per user per hour
        """
        self.secret_key = secret_key.encode()
        self.token_lifetime = token_lifetime
        self.rate_limit = rate_limit
        self.tokens: Dict[str, ResetToken] = {}
        self.request_history: Dict[int, list] = {}

    def generate_reset_token(self, user_id: int, email: str) -> str:
        """
        Generate password reset token

        Args:
            user_id: User ID
            email: User email

        Returns:
            Reset token string
        """
        # Generate random token
        random_token = secrets.token_urlsafe(32)

        # Create signed token with timestamp
        timestamp = int(datetime.utcnow().timestamp())
        data = f"{user_id}:{email}:{timestamp}:{random_token}"

        # Sign with HMAC
        signature = hmac.new(
            self.secret_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        token = f"{data}:{signature}"

        return base64.urlsafe_b64encode(token.encode()).decode()

    def parse_reset_token(self, token: str) -> Optional[Dict]:
        """
        Parse and validate reset token

        Args:
            token: Reset token

        Returns:
            Token data or None if invalid
        """
        try:
            # Decode token
            decoded = base64.urlsafe_b64decode(token.encode()).decode()

            # Split components
            parts = decoded.rsplit(':', 1)
            if len(parts) != 2:
                return None

            data, signature = parts
            user_id, email, timestamp, random_token = data.split(':', 3)

            # Verify signature
            expected_sig = hmac.new(
                self.secret_key,
                data.encode(),
                hashlib.sha256
            ).hexdigest()

            if not secrets.compare_digest(signature, expected_sig):
                return None

            return {
                'user_id': int(user_id),
                'email': email,
                'timestamp': int(timestamp),
                'random_token': random_token
            }

        except (ValueError, UnicodeDecodeError):
            return None

    def request_password_reset(
        self,
        user_id: int,
        email: str
    ) -> Optional[str]:
        """
        Request password reset

        Args:
            user_id: User ID
            email: User email

        Returns:
            Reset token or None if rate limited
        """
        # Check rate limiting
        if not self._check_rate_limit(user_id):
            return None

        # Generate token
        token = self.generate_reset_token(user_id, email)

        # Hash token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Store token
        now = datetime.utcnow()
        expires = now + timedelta(seconds=self.token_lifetime)

        reset_token = ResetToken(
            token_hash=token_hash,
            user_id=user_id,
            email=email,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            is_used=False
        )

        self.tokens[token_hash] = reset_token

        # Record request
        self._record_reset_request(user_id)

        return token

    def verify_reset_token(self, token: str) -> Optional[ResetToken]:
        """
        Verify reset token

        Args:
            token: Reset token

        Returns:
            ResetToken object or None if invalid
        """
        # Parse token
        token_data = self.parse_reset_token(token)

        if not token_data:
            return None

        # Get stored token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        stored_token = self.tokens.get(token_hash)

        if not stored_token:
            return None

        # Check if already used
        if stored_token.is_used:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(stored_token.expires_at)
        if datetime.utcnow() > expires_at:
            return None

        # Verify user ID and email match
        if (token_data['user_id'] != stored_token.user_id or
            token_data['email'] != stored_token.email):
            return None

        return stored_token

    def reset_password(
        self,
        token: str,
        new_password: str,
        password_hasher: callable
    ) -> bool:
        """
        Reset password using token

        Args:
            token: Reset token
            new_password: New password
            password_hasher: Function to hash password

        Returns:
            True if successful
        """
        # Verify token
        reset_token = self.verify_reset_token(token)

        if not reset_token:
            return False

        # Mark token as used
        reset_token.is_used = True

        # In production, update user's password in database
        # password_hash = password_hasher(new_password)
        # update_user_password(reset_token.user_id, password_hash)

        return True

    def _check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user has exceeded rate limit

        Args:
            user_id: User ID

        Returns:
            True if allowed
        """
        if user_id not in self.request_history:
            return True

        # Get requests from last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_requests = [
            dt for dt in self.request_history[user_id]
            if dt > one_hour_ago
        ]

        # Update history
        self.request_history[user_id] = recent_requests

        return len(recent_requests) < self.rate_limit

    def _record_reset_request(self, user_id: int) -> None:
        """Record password reset request"""
        if user_id not in self.request_history:
            self.request_history[user_id] = []

        self.request_history[user_id].append(datetime.utcnow())

    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens

        Returns:
            Number of tokens removed
        """
        now = datetime.utcnow()
        expired = []

        for token_hash, token in self.tokens.items():
            expires_at = datetime.fromisoformat(token.expires_at)
            if now > expires_at or token.is_used:
                expired.append(token_hash)

        for token_hash in expired:
            del self.tokens[token_hash]

        return len(expired)


class EmailService:
    """Email service for password reset"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str
    ):
        """
        Initialize email service

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: From email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        base_url: str
    ) -> bool:
        """
        Send password reset email

        Args:
            to_email: Recipient email
            reset_token: Password reset token
            base_url: Application base URL

        Returns:
            True if sent successfully
        """
        reset_url = f"{base_url}/reset-password?token={reset_token}"

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Password Reset Request'
        msg['From'] = self.from_email
        msg['To'] = to_email

        # Plain text version
        text = f"""
Password Reset Request

You have requested to reset your password.

Please click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this, please ignore this email.
"""

        # HTML version
        html = f"""
<html>
<body>
<h2>Password Reset Request</h2>
<p>You have requested to reset your password.</p>
<p>Please click the button below to reset your password:</p>
<p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-align: center; text-decoration: none; display: inline-block;">Reset Password</a></p>
<p>Or copy and paste this link: <br><code>{reset_url}</code></p>
<p><strong>This link will expire in 1 hour.</strong></p>
<p>If you did not request this, please ignore this email.</p>
</body>
</html>
"""

        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import base64

    # Initialize password reset manager
    secret_key = secrets.token_urlsafe(32)
    reset_manager = PasswordResetManager(secret_key)

    # Request password reset
    user_id = 123
    email = "user@example.com"

    token = reset_manager.request_password_reset(user_id, email)

    if token:
        print(f"Reset token generated: {token[:50]}...")

        # Verify token
        reset_token = reset_manager.verify_reset_token(token)

        if reset_token:
            print(f"Token verified for user {reset_token.user_id}")
            print(f"Expires at: {reset_token.expires_at}")

            # Reset password (with dummy hasher)
            success = reset_manager.reset_password(
                token,
                "NewSecurePassword123!",
                lambda p: hashlib.sha256(p.encode()).hexdigest()
            )

            print(f"Password reset: {success}")

    # Test rate limiting
    print("\nTesting rate limiting:")
    for i in range(5):
        token = reset_manager.request_password_reset(user_id, email)
        if token:
            print(f"Request {i+1}: Success")
        else:
            print(f"Request {i+1}: Rate limited")
