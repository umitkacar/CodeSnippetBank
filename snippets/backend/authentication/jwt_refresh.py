"""JWT Refresh Token Implementation"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from jose import jwt, JWTError


SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_refresh_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise Exception(f"Failed to create refresh token: {str(e)}")


def verify_refresh_token(token: str) -> Optional[Dict]:
    """Verify and decode refresh token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
    except Exception as e:
        raise Exception(f"Failed to verify refresh token: {str(e)}")
