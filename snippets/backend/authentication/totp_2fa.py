"""TOTP 2FA Implementation"""
import pyotp
from typing import Dict, Optional


def generate_secret() -> str:
    """Generate a new TOTP secret"""
    try:
        return pyotp.random_base32()
    except Exception as e:
        raise Exception(f"Failed to generate secret: {str(e)}")


def get_totp_uri(secret: str, name: str, issuer: str = "MyApp") -> str:
    """
    Get TOTP provisioning URI for QR code

    Args:
        secret: TOTP secret
        name: User name/email
        issuer: Application name

    Returns:
        Provisioning URI string
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=name, issuer_name=issuer)
    except Exception as e:
        raise Exception(f"Failed to get TOTP URI: {str(e)}")


def verify_totp(secret: str, token: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP token

    Args:
        secret: TOTP secret
        token: 6-digit TOTP token
        valid_window: Number of time steps to check (default 1)

    Returns:
        True if token is valid, False otherwise
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)
    except Exception as e:
        raise Exception(f"Failed to verify TOTP: {str(e)}")


def get_current_totp(secret: str) -> str:
    """Get current TOTP token"""
    try:
        totp = pyotp.TOTP(secret)
        return totp.now()
    except Exception as e:
        raise Exception(f"Failed to get current TOTP: {str(e)}")
