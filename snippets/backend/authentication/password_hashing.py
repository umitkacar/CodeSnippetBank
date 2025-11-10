"""Password Hashing with bcrypt"""
from typing import Union
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password as a string

    Raises:
        ValueError: If password is empty
    """
    if not password:
        raise ValueError("Password cannot be empty")

    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to hash password: {str(e)}")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Raises:
        ValueError: If password or hash is empty
    """
    if not password or not hashed_password:
        raise ValueError("Password and hash cannot be empty")

    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        raise Exception(f"Failed to verify password: {str(e)}")


def change_password(old_password: str, new_password: str, stored_hash: str) -> str:
    """
    Change password after verifying old password

    Args:
        old_password: Current password
        new_password: New password to set
        stored_hash: Current password hash

    Returns:
        New password hash

    Raises:
        ValueError: If old password doesn't match or new password is invalid
    """
    if not verify_password(old_password, stored_hash):
        raise ValueError("Current password is incorrect")

    if len(new_password) < 8:
        raise ValueError("New password must be at least 8 characters long")

    return hash_password(new_password)


def password_strength_check(password: str) -> dict:
    """
    Check password strength

    Args:
        password: Password to check

    Returns:
        Dictionary with strength information
    """
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    score = sum([has_lower, has_upper, has_digit, has_special])
    strength = "weak"

    if len(password) >= 12 and score >= 3:
        strength = "strong"
    elif len(password) >= 8 and score >= 2:
        strength = "medium"

    return {
        "strength": strength,
        "length": len(password),
        "has_lowercase": has_lower,
        "has_uppercase": has_upper,
        "has_digit": has_digit,
        "has_special": has_special,
        "score": score
    }
