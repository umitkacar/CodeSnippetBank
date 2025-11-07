"""Batch Operations"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
from uuid import UUID, uuid4

app = FastAPI()

class Item(BaseModel):
    id: UUID = None
    name: str
    value: int

class BatchCreateRequest(BaseModel):
    items: List[Item]

class BatchUpdateRequest(BaseModel):
    ids: List[UUID]
    updates: dict

class BatchDeleteRequest(BaseModel):
    ids: List[UUID]

# Storage
items_db = {}

@app.post("/batch/create", status_code=status.HTTP_201_CREATED)
async def batch_create(request: BatchCreateRequest):
    """Create multiple items"""
    created_items = []
    for item in request.items:
        item_id = uuid4()
        item.id = item_id
        items_db[item_id] = item
        created_items.append(item)
    return {"created": len(created_items), "items": created_items}

@app.put("/batch/update")
async def batch_update(request: BatchUpdateRequest):
    """Update multiple items"""
    updated_count = 0
    for item_id in request.ids:
        if item_id in items_db:
            for key, value in request.updates.items():
                setattr(items_db[item_id], key, value)
            updated_count += 1
    return {"updated": updated_count}

@app.delete("/batch/delete")
async def batch_delete(request: BatchDeleteRequest):
    """Delete multiple items"""
    deleted_count = 0
    for item_id in request.ids:
        if item_id in items_db:
            del items_db[item_id]
            deleted_count += 1
    return {"deleted": deleted_count}
