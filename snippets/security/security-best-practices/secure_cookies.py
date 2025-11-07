"""Secure Cookie Configuration"""
from http.cookies import SimpleCookie

class SecureCookies:
    @staticmethod
    def create_secure_cookie(name: str, value: str, max_age: int = 3600) -> str:
        """Create secure cookie"""
        cookie = SimpleCookie()
        cookie[name] = value
        cookie[name]['max-age'] = max_age
        cookie[name]['secure'] = True
        cookie[name]['httponly'] = True
        cookie[name]['samesite'] = 'Strict'
        cookie[name]['path'] = '/'
        return cookie[name].OutputString()

if __name__ == "__main__":
    cookie = SecureCookies.create_secure_cookie('session_id', 'abc123')
    print(f"✓ Secure cookie: {cookie}")
