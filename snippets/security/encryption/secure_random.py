"""
Cryptographically Secure Random Generation
Production-ready secure random utilities
"""
import secrets
import os
from typing import List


class SecureRandom:
    """Secure random generation utilities"""

    @staticmethod
    def generate_token(nbytes: int = 32) -> str:
        """Generate URL-safe token"""
        return secrets.token_urlsafe(nbytes)

    @staticmethod
    def generate_hex(nbytes: int = 32) -> str:
        """Generate hex token"""
        return secrets.token_hex(nbytes)

    @staticmethod
    def generate_bytes(nbytes: int = 32) -> bytes:
        """Generate random bytes"""
        return secrets.token_bytes(nbytes)

    @staticmethod
    def generate_password(length: int = 16, use_special: bool = True) -> str:
        """Generate secure password"""
        import string
        alphabet = string.ascii_letters + string.digits
        if use_special:
            alphabet += string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_pin(length: int = 6) -> str:
        """Generate numeric PIN"""
        return ''.join(str(secrets.randbelow(10)) for _ in range(length))

    @staticmethod
    def shuffle_list(items: List) -> List:
        """Securely shuffle list"""
        items_copy = items.copy()
        for i in range(len(items_copy) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            items_copy[i], items_copy[j] = items_copy[j], items_copy[i]
        return items_copy

    @staticmethod
    def choice(items: List):
        """Securely choose random element"""
        return secrets.choice(items)


# Example
if __name__ == "__main__":
    sr = SecureRandom()
    print(f"Token: {sr.generate_token(16)}")
    print(f"Hex: {sr.generate_hex(16)}")
    print(f"Password: {sr.generate_password(20)}")
    print(f"PIN: {sr.generate_pin(6)}")
    print(f"Random choice: {sr.choice(['A', 'B', 'C', 'D'])}")
