"""OAuth2 Flow Implementation"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
import secrets

app = FastAPI()

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_auth_code = OAuth2AuthorizationCodeBearer(
    authorizationUrl="authorize",
    tokenUrl="token"
)

# Models
class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

class TokenRefresh(BaseModel):
    refresh_token: str

class AuthorizationCode(BaseModel):
    code: str
    redirect_uri: str

class OAuth2Client(BaseModel):
    client_id: str
    client_secret: str
    redirect_uris: List[str]
    allowed_scopes: List[str]

# Mock databases
users_db = {
    "user123": User(
        id="user123",
        username="johndoe",
        email="johndoe@example.com",
        full_name="John Doe",
        scopes=["read", "write"]
    )
}

clients_db = {
    "client123": OAuth2Client(
        client_id="client123",
        client_secret="secret123",
        redirect_uris=["http://localhost:8000/callback"],
        allowed_scopes=["read", "write", "admin"]
    )
}

authorization_codes = {}
refresh_tokens_db = {}

# Token creation functions
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Create refresh token"""
    token = secrets.token_urlsafe(32)
    refresh_tokens_db[token] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return token

def verify_access_token(token: str) -> dict:
    """Verify and decode access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_refresh_token(token: str) -> Optional[str]:
    """Verify refresh token and return user_id"""
    if token not in refresh_tokens_db:
        return None

    token_data = refresh_tokens_db[token]
    if datetime.utcnow() > token_data["expires_at"]:
        del refresh_tokens_db[token]
        return None

    return token_data["user_id"]

# OAuth2 Authorization Code Flow
@app.get("/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str,
    scope: Optional[str] = None,
    state: Optional[str] = None
):
    """OAuth2 authorization endpoint"""
    # Verify client
    if client_id not in clients_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id"
        )

    client = clients_db[client_id]

    # Verify redirect URI
    if redirect_uri not in client.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid redirect_uri"
        )

    # Verify response type
    if response_type != "code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported response_type"
        )

    # Verify scopes
    requested_scopes = scope.split() if scope else []
    if not all(s in client.allowed_scopes for s in requested_scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scope"
        )

    # In production, show login/consent page
    # For demo, auto-approve
    user_id = "user123"
    code = secrets.token_urlsafe(32)

    authorization_codes[code] = {
        "client_id": client_id,
        "user_id": user_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }

    return {
        "message": "Authorization granted",
        "code": code,
        "state": state,
        "redirect_uri": f"{redirect_uri}?code={code}&state={state}"
    }

@app.post("/token", response_model=Token)
async def get_token(
    grant_type: str,
    code: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    refresh_token: Optional[str] = None
):
    """OAuth2 token endpoint"""

    if grant_type == "authorization_code":
        # Verify code
        if not code or code not in authorization_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code"
            )

        code_data = authorization_codes[code]

        # Verify expiration
        if datetime.utcnow() > code_data["expires_at"]:
            del authorization_codes[code]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code expired"
            )

        # Verify client
        if client_id != code_data["client_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client"
            )

        client = clients_db[client_id]
        if client_secret != client.client_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials"
            )

        # Verify redirect URI
        if redirect_uri != code_data["redirect_uri"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid redirect_uri"
            )

        # Generate tokens
        user_id = code_data["user_id"]
        access_token = create_access_token(
            data={"sub": user_id, "scope": code_data["scope"]}
        )
        new_refresh_token = create_refresh_token(user_id)

        # Delete used code
        del authorization_codes[code]

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh_token,
            scope=code_data["scope"]
        )

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing refresh_token"
            )

        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Generate new access token
        access_token = create_access_token(data={"sub": user_id})

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant_type"
        )

# Protected endpoints
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token"""
    payload = verify_access_token(token)
    user_id = payload.get("sub")

    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return users_db[user_id]

def check_scope(required_scopes: List[str]):
    """Check if user has required scopes"""

    async def scope_checker(token: str = Depends(oauth2_scheme)):
        payload = verify_access_token(token)
        token_scopes = payload.get("scope", "").split()

        if not all(scope in token_scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return payload

    return scope_checker

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.get("/protected/read")
async def read_protected(payload: dict = Depends(check_scope(["read"]))):
    """Endpoint requiring read scope"""
    return {"message": "Read access granted", "data": "protected data"}

@app.post("/protected/write")
async def write_protected(payload: dict = Depends(check_scope(["write"]))):
    """Endpoint requiring write scope"""
    return {"message": "Write access granted"}

@app.get("/protected/admin")
async def admin_protected(payload: dict = Depends(check_scope(["admin"]))):
    """Endpoint requiring admin scope"""
    return {"message": "Admin access granted"}

# Token revocation
@app.post("/revoke")
async def revoke_token(token: str, token_type_hint: Optional[str] = None):
    """Revoke access or refresh token"""
    if token_type_hint == "refresh_token" or token in refresh_tokens_db:
        if token in refresh_tokens_db:
            del refresh_tokens_db[token]
            return {"message": "Token revoked successfully"}

    return {"message": "Token revoked"}

# Token introspection
@app.post("/introspect")
async def introspect_token(token: str):
    """Introspect token"""
    try:
        payload = verify_access_token(token)
        return {
            "active": True,
            "user_id": payload.get("sub"),
            "scope": payload.get("scope"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
    except HTTPException:
        return {"active": False}
