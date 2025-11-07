"""Testing Utilities and Test Fixtures"""
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Generator
import pytest

# Main app
app = FastAPI()

# Models
class Item(BaseModel):
    id: int
    name: str
    price: float

# In-memory database
items_db = {}

# Dependency
def get_db():
    """Database dependency"""
    return items_db

# Endpoints
@app.post("/items/", response_model=Item)
def create_item(item: Item, db: dict = Depends(get_db)):
    """Create item"""
    db[item.id] = item
    return item

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: dict = Depends(get_db)):
    """Get item"""
    if item_id not in db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]

@app.get("/items/")
def read_items(db: dict = Depends(get_db)):
    """Get all items"""
    return {"items": list(db.values())}

# Test client
client = TestClient(app)

# Test fixtures
@pytest.fixture
def test_client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def test_db():
    """Test database fixture"""
    db = {}
    yield db
    db.clear()

@pytest.fixture
def sample_item():
    """Sample item fixture"""
    return Item(id=1, name="Test Item", price=9.99)

# Example tests
def test_create_item():
    """Test creating an item"""
    response = client.post(
        "/items/",
        json={"id": 1, "name": "Test Item", "price": 9.99}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"

def test_read_item():
    """Test reading an item"""
    # Create item first
    client.post(
        "/items/",
        json={"id": 1, "name": "Test Item", "price": 9.99}
    )

    # Read item
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_read_nonexistent_item():
    """Test reading a non-existent item"""
    response = client.get("/items/999")
    assert response.status_code == 404

def test_read_all_items():
    """Test reading all items"""
    # Create items
    client.post("/items/", json={"id": 1, "name": "Item 1", "price": 9.99})
    client.post("/items/", json={"id": 2, "name": "Item 2", "price": 19.99})

    # Read all
    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2

# Mock dependencies for testing
def override_get_db():
    """Override database dependency for testing"""
    return {"test": "data"}

app.dependency_overrides[get_db] = override_get_db

# Async tests
@pytest.mark.asyncio
async def test_async_endpoint():
    """Test async endpoint"""
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/items/",
            json={"id": 1, "name": "Async Item", "price": 9.99}
        )
    assert response.status_code == 200

# Parametrized tests
@pytest.mark.parametrize("item_id,name,price", [
    (1, "Item 1", 9.99),
    (2, "Item 2", 19.99),
    (3, "Item 3", 29.99),
])
def test_create_multiple_items(item_id, name, price):
    """Test creating multiple items"""
    response = client.post(
        "/items/",
        json={"id": item_id, "name": name, "price": price}
    )
    assert response.status_code == 200
    assert response.json()["id"] == item_id
