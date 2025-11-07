"""Database Connection Pooling"""
from fastapi import FastAPI, Depends
from typing import Generator
import asyncio

app = FastAPI()

class ConnectionPool:
    def __init__(self, min_size: int = 5, max_size: int = 20):
        self.min_size = min_size
        self.max_size = max_size
        self.connections = []
        self.in_use = set()

    async def acquire(self):
        """Acquire connection from pool"""
        if self.connections:
            conn = self.connections.pop()
        elif len(self.in_use) < self.max_size:
            conn = await self.create_connection()
        else:
            # Wait for available connection
            while not self.connections:
                await asyncio.sleep(0.1)
            conn = self.connections.pop()

        self.in_use.add(conn)
        return conn

    async def release(self, conn):
        """Release connection back to pool"""
        self.in_use.remove(conn)
        if len(self.connections) < self.min_size:
            self.connections.append(conn)
        else:
            await self.close_connection(conn)

    async def create_connection(self):
        """Create new database connection"""
        return {"id": len(self.connections), "active": True}

    async def close_connection(self, conn):
        """Close database connection"""
        conn["active"] = False

pool = ConnectionPool()

async def get_db_connection():
    """Get database connection from pool"""
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)

@app.get("/query")
async def execute_query(conn = Depends(get_db_connection)):
    """Execute query with pooled connection"""
    return {"connection_id": conn["id"], "result": "Query executed"}
