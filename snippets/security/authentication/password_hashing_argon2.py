"""
Password Hashing with Argon2
Production-ready password hashing using Argon2id (recommended by OWASP)
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from typing import Optional


class Argon2PasswordManager:
    """Secure password hashing using Argon2id"""

    def __init__(
        self,
        time_cost: int = 2,
        memory_cost: int = 65536,  # 64 MB
        parallelism: int = 4,
        hash_len: int = 32,
        salt_len: int = 16
    ):
        """
        Initialize Argon2 password hasher

        Args:
            time_cost: Number of iterations (default 2)
            memory_cost: Memory usage in KiB (default 65536 = 64MB)
            parallelism: Number of parallel threads (default 4)
            hash_len: Length of hash in bytes (default 32)
            salt_len: Length of salt in bytes (default 16)
        """
        self.ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len
        )

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return self.ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            password: Plain text password
            hashed_password: Stored hash

        Returns:
            True if password matches
        """
        try:
            self.ph.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
        except (VerificationError, InvalidHash) as e:
            print(f"Hash verification error: {e}")
            return False

    def check_needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if password hash needs updating

        Args:
            hashed_password: Stored hash

        Returns:
            True if rehash recommended
        """
        try:
            return self.ph.check_needs_rehash(hashed_password)
        except Exception:
            return True

    def verify_and_update(
        self,
        password: str,
        hashed_password: str
    ) -> tuple[bool, Optional[str]]:
        """
        Verify password and return new hash if update needed

        Args:
            password: Plain text password
            hashed_password: Current hash

        Returns:
            Tuple of (is_valid, new_hash_if_needed)
        """
        try:
            # Verify password
            self.ph.verify(hashed_password, password)

            # Check if rehash needed
            if self.check_needs_rehash(hashed_password):
                new_hash = self.hash_password(password)
                return True, new_hash
            else:
                return True, None

        except VerifyMismatchError:
            return False, None
        except Exception as e:
            print(f"Error during verification: {e}")
            return False, None


class SecurePasswordPolicy:
    """Password policy enforcement"""

    def __init__(
        self,
        min_length: int = 12,
        max_length: int = 128,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        min_unique_chars: int = 5
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.min_unique_chars = min_unique_chars

    def validate(self, password: str) -> tuple[bool, list[str]]:
        """
        Validate password against policy

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Length check
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")

        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")

        # Character requirements
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")

        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")

        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")

        if self.require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")

        # Unique characters check
        unique_chars = len(set(password))
        if unique_chars < self.min_unique_chars:
            errors.append(
                f"Password must contain at least {self.min_unique_chars} unique characters"
            )

        # Common password check (basic)
        common_passwords = [
            "password", "123456", "qwerty", "admin", "letmein",
            "welcome", "monkey", "dragon", "master", "sunshine"
        ]
        if password.lower() in common_passwords:
            errors.append("Password is too common")

        return len(errors) == 0, errors

    def check_password_history(
        self,
        password: str,
        previous_hashes: list[str],
        hasher: Argon2PasswordManager
    ) -> bool:
        """
        Check if password was used before

        Args:
            password: New password
            previous_hashes: List of previous password hashes
            hasher: Argon2PasswordManager instance

        Returns:
            True if password is new (not in history)
        """
        for prev_hash in previous_hashes:
            if hasher.verify_password(password, prev_hash):
                return False
        return True


# Example usage
if __name__ == "__main__":
    # Initialize Argon2 password manager
    pwd_manager = Argon2PasswordManager()

    # Hash a password
    password = "MyS3cur3P@ssw0rd!"
    hashed = pwd_manager.hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")

    # Verify password
    is_valid = pwd_manager.verify_password(password, hashed)
    print(f"Password valid: {is_valid}")

    # Check if rehash needed
    needs_rehash = pwd_manager.check_needs_rehash(hashed)
    print(f"Needs rehash: {needs_rehash}")

    # Verify and update
    is_valid, new_hash = pwd_manager.verify_and_update(password, hashed)
    print(f"Verify and update: valid={is_valid}, new_hash={new_hash}")

    # Test password policy
    policy = SecurePasswordPolicy()
    is_valid, errors = policy.validate(password)
    print(f"\nPassword policy validation: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")

    # Test weak password
    weak_password = "weak"
    is_valid, errors = policy.validate(weak_password)
    print(f"\nWeak password validation: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
