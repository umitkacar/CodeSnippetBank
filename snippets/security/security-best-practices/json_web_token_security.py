"""JWT Security Best Practices"""
import jwt
from datetime import datetime, timedelta

class JWTSecurity:
    """Secure JWT handling"""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret = secret_key
        self.algorithm = algorithm
    
    def create_token(self, payload: dict, expires_minutes: int = 15) -> str:
        """Create secure JWT"""
        exp = datetime.utcnow() + timedelta(minutes=expires_minutes)
        payload.update({
            'exp': exp,
            'iat': datetime.utcnow(),
            'nbf': datetime.utcnow()
        })
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT with all checks"""
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True
                }
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

if __name__ == "__main__":
    jwt_sec = JWTSecurity("secret_key")
    token = jwt_sec.create_token({'user_id': 123})
    print(f"✓ JWT created: {token[:30]}...")
