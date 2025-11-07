"""CORS Configuration"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Advanced CORS with specific methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    expose_headers=["X-Total-Count", "X-Page-Number"],
    max_age=600,
)

@app.get("/api/data")
async def get_data():
    """CORS-enabled endpoint"""
    return {"data": "This endpoint supports CORS"}

@app.options("/api/data")
async def options_data():
    """Handle preflight requests"""
    return {"methods": ["GET", "POST", "PUT", "DELETE"]}
