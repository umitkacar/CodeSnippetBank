"""CORS Configuration"""
from typing import List, Optional

class CORSConfig:
    def __init__(
        self,
        allowed_origins: List[str] = None,
        allowed_methods: List[str] = None,
        allowed_headers: List[str] = None,
        max_age: int = 3600,
        allow_credentials: bool = False
    ):
        self.allowed_origins = allowed_origins or []
        self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE']
        self.allowed_headers = allowed_headers or ['Content-Type', 'Authorization']
        self.max_age = max_age
        self.allow_credentials = allow_credentials
    
    def get_headers(self, origin: str = None) -> dict:
        """Get CORS headers"""
        headers = {}
        
        if origin and self.is_origin_allowed(origin):
            headers['Access-Control-Allow-Origin'] = origin
        elif '*' in self.allowed_origins:
            headers['Access-Control-Allow-Origin'] = '*'
        
        headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
        headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        headers['Access-Control-Max-Age'] = str(self.max_age)
        
        if self.allow_credentials:
            headers['Access-Control-Allow-Credentials'] = 'true'
        
        return headers
    
    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        return origin in self.allowed_origins or '*' in self.allowed_origins

if __name__ == "__main__":
    cors = CORSConfig(
        allowed_origins=['https://example.com', 'https://app.example.com'],
        allow_credentials=True
    )
    headers = cors.get_headers('https://example.com')
    print("✓ CORS Headers:", headers)
