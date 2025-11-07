"""Password Policy Enforcement"""
import re

class PasswordPolicy:
    def __init__(
        self,
        min_length: int = 12,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        min_unique_chars: int = 5
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.min_unique_chars = min_unique_chars
    
    def validate(self, password: str) -> tuple[bool, list[str]]:
        """Validate password against policy"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        
        if self.require_digit and not re.search(r'\d', password):
            errors.append("Password must contain digits")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special characters")
        
        if len(set(password)) < self.min_unique_chars:
            errors.append(f"Password must contain at least {self.min_unique_chars} unique characters")
        
        return len(errors) == 0, errors

if __name__ == "__main__":
    policy = PasswordPolicy()
    valid, errors = policy.validate("MyP@ssw0rd123")
    print(f"✓ Valid: {valid}")
    if errors:
        for error in errors:
            print(f"  - {error}")
