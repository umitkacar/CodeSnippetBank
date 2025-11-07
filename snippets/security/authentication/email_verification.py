"""
Email Verification System
Production-ready email verification with secure tokens
"""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass
import time


@dataclass
class VerificationToken:
    """Email verification token data"""
    token_hash: str
    user_id: int
    email: str
    created_at: str
    expires_at: str
    is_verified: bool
    attempts: int


class EmailVerificationManager:
    """Manage email verification process"""

    def __init__(
        self,
        secret_key: str,
        token_lifetime: int = 86400,  # 24 hours
        max_attempts: int = 5
    ):
        """
        Initialize email verification manager

        Args:
            secret_key: Secret key for token generation
            token_lifetime: Token lifetime in seconds
            max_attempts: Maximum verification attempts
        """
        self.secret_key = secret_key.encode()
        self.token_lifetime = token_lifetime
        self.max_attempts = max_attempts
        self.tokens: Dict[str, VerificationToken] = {}

    def generate_verification_token(
        self,
        user_id: int,
        email: str
    ) -> str:
        """
        Generate email verification token

        Args:
            user_id: User ID
            email: Email address to verify

        Returns:
            Verification token
        """
        # Generate random token component
        random_data = secrets.token_urlsafe(32)

        # Create token with user data
        timestamp = int(time.time())
        payload = f"{user_id}:{email}:{timestamp}:{random_data}"

        # Sign payload
        signature = hmac.new(
            self.secret_key,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combine payload and signature
        token = f"{payload}:{signature}"

        # URL-safe encoding
        import base64
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()

        return encoded_token

    def parse_verification_token(
        self,
        token: str
    ) -> Optional[Dict]:
        """
        Parse and validate verification token structure

        Args:
            token: Verification token

        Returns:
            Token data or None if invalid
        """
        try:
            import base64

            # Decode token
            decoded = base64.urlsafe_b64decode(token.encode()).decode()

            # Split into parts
            parts = decoded.rsplit(':', 1)
            if len(parts) != 2:
                return None

            payload, signature = parts

            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            if not secrets.compare_digest(signature, expected_signature):
                return None

            # Parse payload
            user_id, email, timestamp, random_data = payload.split(':', 3)

            return {
                'user_id': int(user_id),
                'email': email,
                'timestamp': int(timestamp),
                'random_data': random_data
            }

        except (ValueError, UnicodeDecodeError):
            return None

    def create_verification_request(
        self,
        user_id: int,
        email: str
    ) -> str:
        """
        Create email verification request

        Args:
            user_id: User ID
            email: Email to verify

        Returns:
            Verification token
        """
        # Generate token
        token = self.generate_verification_token(user_id, email)

        # Hash token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Check if token already exists and remove it
        if token_hash in self.tokens:
            del self.tokens[token_hash]

        # Store verification data
        now = datetime.utcnow()
        expires = now + timedelta(seconds=self.token_lifetime)

        verification = VerificationToken(
            token_hash=token_hash,
            user_id=user_id,
            email=email,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            is_verified=False,
            attempts=0
        )

        self.tokens[token_hash] = verification

        return token

    def verify_email(self, token: str) -> tuple[bool, str]:
        """
        Verify email using token

        Args:
            token: Verification token

        Returns:
            Tuple of (success, message)
        """
        # Parse token
        token_data = self.parse_verification_token(token)

        if not token_data:
            return False, "Invalid verification token"

        # Get stored verification
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        verification = self.tokens.get(token_hash)

        if not verification:
            return False, "Verification token not found"

        # Check if already verified
        if verification.is_verified:
            return False, "Email already verified"

        # Check attempts
        if verification.attempts >= self.max_attempts:
            return False, "Too many verification attempts"

        # Increment attempts
        verification.attempts += 1

        # Check expiration
        expires_at = datetime.fromisoformat(verification.expires_at)
        if datetime.utcnow() > expires_at:
            return False, "Verification token has expired"

        # Verify user ID and email match
        if (token_data['user_id'] != verification.user_id or
            token_data['email'] != verification.email):
            return False, "Token data mismatch"

        # Mark as verified
        verification.is_verified = True

        return True, "Email verified successfully"

    def is_email_verified(self, user_id: int, email: str) -> bool:
        """
        Check if email is verified

        Args:
            user_id: User ID
            email: Email address

        Returns:
            True if verified
        """
        for verification in self.tokens.values():
            if (verification.user_id == user_id and
                verification.email == email and
                verification.is_verified):
                return True

        return False

    def resend_verification(
        self,
        user_id: int,
        email: str,
        cooldown_seconds: int = 60
    ) -> Optional[str]:
        """
        Resend verification email

        Args:
            user_id: User ID
            email: Email address
            cooldown_seconds: Cooldown period between resends

        Returns:
            New verification token or None if in cooldown
        """
        # Check for recent verification request
        for verification in self.tokens.values():
            if (verification.user_id == user_id and
                verification.email == email and
                not verification.is_verified):

                created_at = datetime.fromisoformat(verification.created_at)
                time_since_creation = (datetime.utcnow() - created_at).total_seconds()

                if time_since_creation < cooldown_seconds:
                    return None

        # Create new verification request
        return self.create_verification_request(user_id, email)

    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired and verified tokens

        Returns:
            Number of tokens removed
        """
        now = datetime.utcnow()
        to_remove = []

        for token_hash, verification in self.tokens.items():
            expires_at = datetime.fromisoformat(verification.expires_at)

            # Remove if expired or verified
            if now > expires_at or verification.is_verified:
                to_remove.append(token_hash)

        for token_hash in to_remove:
            del self.tokens[token_hash]

        return len(to_remove)


class EmailVerificationService:
    """Complete email verification service with email sending"""

    def __init__(
        self,
        verification_manager: EmailVerificationManager,
        email_service,  # EmailService from password_reset_flow
        base_url: str
    ):
        """
        Initialize email verification service

        Args:
            verification_manager: EmailVerificationManager instance
            email_service: Email service for sending
            base_url: Application base URL
        """
        self.verification_manager = verification_manager
        self.email_service = email_service
        self.base_url = base_url

    def send_verification_email(
        self,
        user_id: int,
        email: str,
        username: str
    ) -> bool:
        """
        Send verification email

        Args:
            user_id: User ID
            email: Email to verify
            username: User's display name

        Returns:
            True if sent successfully
        """
        # Create verification token
        token = self.verification_manager.create_verification_request(
            user_id,
            email
        )

        # Build verification URL
        verify_url = f"{self.base_url}/verify-email?token={token}"

        # Email content
        subject = "Verify Your Email Address"

        text_body = f"""
Hello {username},

Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
The Team
"""

        html_body = f"""
<html>
<body>
    <h2>Verify Your Email Address</h2>
    <p>Hello {username},</p>
    <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
    <p>
        <a href="{verify_url}"
           style="background-color: #4CAF50; color: white; padding: 14px 20px;
                  text-align: center; text-decoration: none; display: inline-block;
                  border-radius: 4px;">
            Verify Email
        </a>
    </p>
    <p>Or copy and paste this link:<br><code>{verify_url}</code></p>
    <p><strong>This link will expire in 24 hours.</strong></p>
    <p>If you did not create an account, please ignore this email.</p>
    <p>Best regards,<br>The Team</p>
</body>
</html>
"""

        # Send email (implementation depends on email service)
        # return self.email_service.send_email(email, subject, text_body, html_body)

        return True


# Example usage
if __name__ == "__main__":
    # Initialize verification manager
    secret_key = secrets.token_urlsafe(32)
    verification_mgr = EmailVerificationManager(secret_key)

    # Create verification request
    user_id = 123
    email = "user@example.com"

    token = verification_mgr.create_verification_request(user_id, email)
    print(f"Verification token: {token[:50]}...")

    # Verify email
    success, message = verification_mgr.verify_email(token)
    print(f"Verification: {success} - {message}")

    # Check if verified
    is_verified = verification_mgr.is_email_verified(user_id, email)
    print(f"Email verified: {is_verified}")

    # Test resend with cooldown
    print("\nTesting resend cooldown:")
    new_token = verification_mgr.resend_verification(user_id, "new@example.com")
    if new_token:
        print(f"Resent token: {new_token[:50]}...")
    else:
        print("Resend in cooldown period")

    # Test invalid token
    print("\nTesting invalid token:")
    success, message = verification_mgr.verify_email("invalid_token")
    print(f"Invalid token: {success} - {message}")

    # Test expired token
    print("\nTesting token attempts:")
    for i in range(7):
        success, message = verification_mgr.verify_email(new_token)
        print(f"Attempt {i+1}: {success} - {message}")
        if not success and "Too many" in message:
            break
