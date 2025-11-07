"""
Multi-Factor Authentication (TOTP) Implementation
Production-ready 2FA with Time-based One-Time Password
"""
import pyotp
import qrcode
import io
import base64
from typing import Optional, Tuple
from datetime import datetime


class TOTPAuthenticator:
    """TOTP-based Multi-Factor Authentication"""

    def __init__(self, issuer_name: str = "MyApp"):
        self.issuer_name = issuer_name

    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret key

        Returns:
            Base32-encoded secret key
        """
        return pyotp.random_base32()

    def get_provisioning_uri(
        self,
        secret: str,
        user_identifier: str,
        issuer_name: Optional[str] = None
    ) -> str:
        """
        Generate provisioning URI for QR code

        Args:
            secret: TOTP secret key
            user_identifier: User email or username
            issuer_name: Optional issuer name override

        Returns:
            Provisioning URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_identifier,
            issuer_name=issuer_name or self.issuer_name
        )

    def generate_qr_code(
        self,
        secret: str,
        user_identifier: str
    ) -> str:
        """
        Generate QR code as base64 string

        Args:
            secret: TOTP secret key
            user_identifier: User email or username

        Returns:
            Base64-encoded QR code image
        """
        uri = self.get_provisioning_uri(secret, user_identifier)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_token(
        self,
        secret: str,
        token: str,
        valid_window: int = 1
    ) -> bool:
        """
        Verify TOTP token

        Args:
            secret: TOTP secret key
            token: 6-digit TOTP code from user
            valid_window: Number of time steps to check (default 1 = 30s window)

        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)

    def get_current_token(self, secret: str) -> str:
        """
        Get current TOTP token (for testing)

        Args:
            secret: TOTP secret key

        Returns:
            Current 6-digit token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()

    def get_time_remaining(self) -> int:
        """
        Get seconds remaining until next token

        Returns:
            Seconds until token expires
        """
        return 30 - (int(datetime.now().timestamp()) % 30)


class BackupCodes:
    """Backup codes for account recovery"""

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """
        Generate backup recovery codes

        Args:
            count: Number of codes to generate

        Returns:
            List of backup codes
        """
        import secrets
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(
                secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
                for _ in range(8)
            )
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        Hash backup code for storage

        Args:
            code: Plain backup code

        Returns:
            Hashed code
        """
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """
        Verify backup code

        Args:
            code: Plain code from user
            hashed_code: Stored hashed code

        Returns:
            True if code matches
        """
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest() == hashed_code


# Example usage
if __name__ == "__main__":
    authenticator = TOTPAuthenticator(issuer_name="MySecureApp")

    # Setup 2FA for a user
    user_email = "user@example.com"
    secret = authenticator.generate_secret()
    print(f"Secret key: {secret}")

    # Generate QR code
    qr_code = authenticator.generate_qr_code(secret, user_email)
    print(f"QR Code (base64): {qr_code[:50]}...")

    # Get current token (for testing)
    current_token = authenticator.get_current_token(secret)
    print(f"Current token: {current_token}")

    # Verify token
    is_valid = authenticator.verify_token(secret, current_token)
    print(f"Token valid: {is_valid}")

    # Generate backup codes
    backup_codes = BackupCodes.generate_backup_codes()
    print(f"\nBackup codes: {backup_codes}")

    # Hash backup codes for storage
    hashed_codes = [BackupCodes.hash_backup_code(code) for code in backup_codes]
    print(f"First hashed code: {hashed_codes[0]}")
