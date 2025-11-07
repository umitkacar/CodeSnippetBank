"""Social Authentication"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import secrets

app = FastAPI()

class SocialAuthRequest(BaseModel):
    provider: str
    access_token: str

class SocialUserInfo(BaseModel):
    provider: str
    provider_id: str
    email: str
    name: str

async def verify_google_token(access_token: str) -> SocialUserInfo:
    """Verify Google OAuth token"""
    # In production, verify with Google API
    return SocialUserInfo(
        provider="google",
        provider_id="google_123",
        email="user@gmail.com",
        name="Google User"
    )

async def verify_github_token(access_token: str) -> SocialUserInfo:
    """Verify GitHub OAuth token"""
    # In production, verify with GitHub API
    return SocialUserInfo(
        provider="github",
        provider_id="github_123",
        email="user@github.com",
        name="GitHub User"
    )

@app.post("/auth/social")
async def social_auth(auth_request: SocialAuthRequest):
    """Authenticate with social provider"""
    if auth_request.provider == "google":
        user_info = await verify_google_token(auth_request.access_token)
    elif auth_request.provider == "github":
        user_info = await verify_github_token(auth_request.access_token)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Create or update user in database
    session_token = secrets.token_urlsafe(32)

    return {
        "token": session_token,
        "user": user_info.model_dump()
    }

@app.get("/auth/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback"""
    # Exchange code for access token
    return {"message": "Google authentication successful"}

@app.get("/auth/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback"""
    # Exchange code for access token
    return {"message": "GitHub authentication successful"}
