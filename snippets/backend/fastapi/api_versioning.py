"""API Versioning Strategies"""
from fastapi import FastAPI, APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional

# Main app
app = FastAPI()

# Models for different versions
class UserV1(BaseModel):
    id: int
    name: str
    email: str

class UserV2(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

# Strategy 1: URL Path Versioning
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v1_router.get("/users/{user_id}", response_model=UserV1)
async def get_user_v1(user_id: int):
    """Get user - Version 1"""
    return UserV1(
        id=user_id,
        name="John Doe",
        email="john@example.com"
    )

@v2_router.get("/users/{user_id}", response_model=UserV2)
async def get_user_v2(user_id: int):
    """Get user - Version 2 with enhanced fields"""
    return UserV2(
        id=user_id,
        username="johndoe",
        email="john@example.com",
        full_name="John Doe",
        is_active=True
    )

app.include_router(v1_router)
app.include_router(v2_router)

# Strategy 2: Header-based Versioning
@app.get("/users/{user_id}")
async def get_user_header_version(
    user_id: int,
    api_version: str = Header(default="v1", alias="X-API-Version")
):
    """Get user with header-based versioning"""
    if api_version == "v1":
        return UserV1(
            id=user_id,
            name="John Doe",
            email="john@example.com"
        )
    elif api_version == "v2":
        return UserV2(
            id=user_id,
            username="johndoe",
            email="john@example.com",
            full_name="John Doe",
            is_active=True
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported API version: {api_version}"
        )

# Strategy 3: Query Parameter Versioning
@app.get("/products/{product_id}")
async def get_product(product_id: int, version: str = "v1"):
    """Get product with query parameter versioning"""
    if version == "v1":
        return {
            "id": product_id,
            "name": "Product Name",
            "price": 99.99
        }
    elif version == "v2":
        return {
            "id": product_id,
            "name": "Product Name",
            "price": 99.99,
            "currency": "USD",
            "stock": 100
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported version: {version}"
        )

# Deprecation warnings
@v1_router.get("/deprecated-endpoint")
async def deprecated_endpoint():
    """Deprecated endpoint with warning header"""
    from fastapi.responses import JSONResponse

    response = JSONResponse(content={"message": "This endpoint is deprecated"})
    response.headers["Warning"] = '299 - "This API version is deprecated. Please migrate to v2"'
    response.headers["X-API-Deprecation-Date"] = "2024-12-31"
    response.headers["X-API-Migration-Guide"] = "https://api.example.com/docs/migration-v2"

    return response

# Version negotiation
def negotiate_version(accept_version: Optional[str]) -> str:
    """Negotiate API version based on Accept-Version header"""
    if not accept_version:
        return "v1"  # Default version

    # Parse version preference
    versions = [v.strip() for v in accept_version.split(",")]

    # Return highest supported version
    supported_versions = ["v1", "v2"]
    for version in versions:
        if version in supported_versions:
            return version

    return "v1"  # Fallback to default

@app.get("/negotiated/{item_id}")
async def get_item_negotiated(
    item_id: int,
    accept_version: Optional[str] = Header(None, alias="Accept-Version")
):
    """Get item with version negotiation"""
    version = negotiate_version(accept_version)

    if version == "v1":
        return {"id": item_id, "data": "v1 data"}
    else:
        return {"id": item_id, "data": "v2 data", "extra": "v2 field"}
