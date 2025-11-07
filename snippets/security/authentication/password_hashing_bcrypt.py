"""
Password Hashing with bcrypt
Production-ready password hashing and verification
"""
import bcrypt
from typing import Optional


class BcryptPasswordManager:
    """Secure password hashing using bcrypt"""

    def __init__(self, rounds: int = 12):
        """
        Initialize password manager

        Args:
            rounds: Cost factor (4-31, default 12)
                   Higher = more secure but slower
                   12 = ~0.3s, 14 = ~1.2s
        """
        if rounds < 4 or rounds > 31:
            raise ValueError("Rounds must be between 4 and 31")
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        """
        Hash a password

        Args:
            password: Plain text password

        Returns:
            Hashed password (includes salt)
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            password: Plain text password to verify
            hashed_password: Stored hash

        Returns:
            True if password matches
        """
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')

            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            print(f"Verification error: {e}")
            return False

    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if password needs rehashing (cost factor changed)

        Args:
            hashed_password: Stored hash

        Returns:
            True if rehash needed
        """
        try:
            # Extract current rounds from hash
            hashed_bytes = hashed_password.encode('utf-8')
            # bcrypt hash format: $2b$rounds$salt+hash
            parts = hashed_bytes.split(b'$')
            if len(parts) >= 3:
                current_rounds = int(parts[2])
                return current_rounds != self.rounds
            return True
        except:
            return True

    def update_password(
        self,
        password: str,
        old_hash: str
    ) -> Optional[str]:
        """
        Update password hash if needed

        Args:
            password: Plain text password
            old_hash: Current hash

        Returns:
            New hash if update needed, None otherwise
        """
        if self.verify_password(password, old_hash):
            if self.needs_rehash(old_hash):
                return self.hash_password(password)
        return None


class PasswordStrengthValidator:
    """Validate password strength"""

    @staticmethod
    def check_strength(password: str) -> dict:
        """
        Check password strength

        Args:
            password: Password to check

        Returns:
            Dictionary with strength metrics
        """
        import re

        strength = {
            "length": len(password),
            "has_lowercase": bool(re.search(r'[a-z]', password)),
            "has_uppercase": bool(re.search(r'[A-Z]', password)),
            "has_digit": bool(re.search(r'\d', password)),
            "has_special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            "score": 0,
            "is_strong": False
        }

        # Calculate score
        if strength["length"] >= 8:
            strength["score"] += 1
        if strength["length"] >= 12:
            strength["score"] += 1
        if strength["length"] >= 16:
            strength["score"] += 1

        strength["score"] += sum([
            strength["has_lowercase"],
            strength["has_uppercase"],
            strength["has_digit"],
            strength["has_special"]
        ])

        # Strong password: length >= 12 and at least 3 character types
        char_types = sum([
            strength["has_lowercase"],
            strength["has_uppercase"],
            strength["has_digit"],
            strength["has_special"]
        ])

        strength["is_strong"] = strength["length"] >= 12 and char_types >= 3

        return strength

    @staticmethod
    def validate_password(password: str, min_length: int = 12) -> tuple:
        """
        Validate password meets requirements

        Args:
            password: Password to validate
            min_length: Minimum length required

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"

        strength = PasswordStrengthValidator.check_strength(password)

        if not strength["has_uppercase"]:
            return False, "Password must contain uppercase letters"

        if not strength["has_lowercase"]:
            return False, "Password must contain lowercase letters"

        if not strength["has_digit"]:
            return False, "Password must contain digits"

        if not strength["has_special"]:
            return False, "Password must contain special characters"

        return True, "Password is valid"


# Example usage
if __name__ == "__main__":
    # Initialize password manager
    pwd_manager = BcryptPasswordManager(rounds=12)

    # Hash a password
    password = "SecureP@ssw0rd123"
    hashed = pwd_manager.hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")

    # Verify password
    is_valid = pwd_manager.verify_password(password, hashed)
    print(f"Password valid: {is_valid}")

    # Verify wrong password
    is_valid = pwd_manager.verify_password("WrongPassword", hashed)
    print(f"Wrong password valid: {is_valid}")

    # Check password strength
    validator = PasswordStrengthValidator()
    strength = validator.check_strength(password)
    print(f"\nPassword strength: {strength}")

    # Validate password
    is_valid, message = validator.validate_password(password)
    print(f"Validation: {is_valid} - {message}")

    # Test weak password
    weak_password = "weak"
    is_valid, message = validator.validate_password(weak_password)
    print(f"Weak password validation: {is_valid} - {message}")
