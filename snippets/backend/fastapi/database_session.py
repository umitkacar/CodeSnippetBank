"""Database Session Management"""
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Generator, Optional
from contextlib import contextmanager

app = FastAPI()

# Database connection pool simulation
class DatabasePool:
    """Database connection pool"""

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = []

    def get_connection(self):
        """Get connection from pool"""
        if len(self.connections) < self.max_connections:
            connection = {"id": len(self.connections), "active": True}
            self.connections.append(connection)
            return connection
        raise Exception("Connection pool exhausted")

    def release_connection(self, connection):
        """Release connection back to pool"""
        connection["active"] = False

db_pool = DatabasePool()

# Session dependency
class DatabaseSession:
    """Database session"""

    def __init__(self, connection):
        self.connection = connection
        self.transaction_active = False

    def begin_transaction(self):
        """Begin transaction"""
        self.transaction_active = True

    def commit(self):
        """Commit transaction"""
        if self.transaction_active:
            print("Transaction committed")
            self.transaction_active = False

    def rollback(self):
        """Rollback transaction"""
        if self.transaction_active:
            print("Transaction rolled back")
            self.transaction_active = False

    def close(self):
        """Close session"""
        if self.transaction_active:
            self.rollback()
        db_pool.release_connection(self.connection)

def get_db_session() -> Generator[DatabaseSession, None, None]:
    """Database session dependency"""
    connection = db_pool.get_connection()
    session = DatabaseSession(connection)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Models
class Item(BaseModel):
    id: int
    name: str

# Endpoints with database session
@app.post("/items/")
async def create_item(
    item: Item,
    db: DatabaseSession = Depends(get_db_session)
):
    """Create item with database session"""
    db.begin_transaction()
    # Simulate database operation
    return {"message": "Item created", "item": item}

@app.get("/items/{item_id}")
async def get_item(
    item_id: int,
    db: DatabaseSession = Depends(get_db_session)
):
    """Get item with database session"""
    # Simulate database query
    return {"item_id": item_id, "name": f"Item {item_id}"}

# Transaction management
@contextmanager
def transaction(session: DatabaseSession):
    """Transaction context manager"""
    session.begin_transaction()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

@app.post("/items-transactional/")
async def create_item_transactional(
    item: Item,
    db: DatabaseSession = Depends(get_db_session)
):
    """Create item with explicit transaction"""
    with transaction(db):
        # Database operations here
        return {"message": "Item created in transaction", "item": item}
