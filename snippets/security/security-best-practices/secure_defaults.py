"""Secure Defaults"""
class SecureDefaults:
    @staticmethod
    def get_defaults():
        return {
            'https_only': True,
            'secure_cookies': True,
            'csrf_protection': True,
            'rate_limiting': True
        }
