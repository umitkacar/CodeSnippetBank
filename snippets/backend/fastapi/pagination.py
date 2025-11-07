"""Pagination Patterns"""
from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar
from math import ceil

app = FastAPI()

# Models
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

# Generate sample data
items_db = [
    Item(id=i, name=f"Item {i}", description=f"Description for item {i}", price=10.0 + i)
    for i in range(1, 101)
]

# Pagination Models
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response"""
    items: List[T]
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None
    has_next: bool
    has_previous: bool

class OffsetPaginatedResponse(BaseModel, Generic[T]):
    """Offset-based paginated response"""
    items: List[T]
    total: int
    offset: int
    limit: int

# Basic Offset Pagination
@app.get("/items/offset", response_model=OffsetPaginatedResponse[Item])
async def get_items_offset(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return")
):
    """Get items with offset pagination"""
    total = len(items_db)
    items = items_db[offset:offset + limit]

    return OffsetPaginatedResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit
    )

# Page-based Pagination
@app.get("/items/page", response_model=PaginatedResponse[Item])
async def get_items_page(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get items with page-based pagination"""
    total = len(items_db)
    total_pages = ceil(total / page_size)

    if page > total_pages and total > 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page} does not exist. Total pages: {total_pages}"
        )

    start = (page - 1) * page_size
    end = start + page_size
    items = items_db[start:end]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )

# Cursor-based Pagination
import base64
import json

def encode_cursor(item_id: int) -> str:
    """Encode cursor"""
    cursor_data = {"id": item_id}
    cursor_json = json.dumps(cursor_data)
    return base64.b64encode(cursor_json.encode()).decode()

def decode_cursor(cursor: str) -> int:
    """Decode cursor"""
    try:
        cursor_json = base64.b64decode(cursor.encode()).decode()
        cursor_data = json.loads(cursor_json)
        return cursor_data["id"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cursor"
        )

@app.get("/items/cursor", response_model=CursorPaginatedResponse[Item])
async def get_items_cursor(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    direction: str = Query("next", regex="^(next|previous)$", description="Direction of pagination")
):
    """Get items with cursor-based pagination"""
    if cursor:
        cursor_id = decode_cursor(cursor)
        cursor_index = next((i for i, item in enumerate(items_db) if item.id == cursor_id), None)

        if cursor_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cursor item not found"
            )

        if direction == "next":
            start = cursor_index + 1
            end = start + limit
            items = items_db[start:end]
        else:  # previous
            end = cursor_index
            start = max(0, end - limit)
            items = items_db[start:end]
    else:
        items = items_db[:limit]

    # Generate cursors
    next_cursor = None
    previous_cursor = None

    if items:
        if direction == "next":
            last_item = items[-1]
            last_index = next(i for i, item in enumerate(items_db) if item.id == last_item.id)
            has_next = last_index < len(items_db) - 1
            has_previous = cursor is not None or len(items) > 0

            if has_next:
                next_cursor = encode_cursor(last_item.id)
            if has_previous and items:
                previous_cursor = encode_cursor(items[0].id)
        else:
            first_item = items[0]
            first_index = next(i for i, item in enumerate(items_db) if item.id == first_item.id)
            has_next = cursor is not None
            has_previous = first_index > 0

            if has_next:
                next_cursor = encode_cursor(items[-1].id)
            if has_previous:
                previous_cursor = encode_cursor(first_item.id)
    else:
        has_next = False
        has_previous = False

    return CursorPaginatedResponse(
        items=items,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
        has_next=has_next,
        has_previous=has_previous
    )

# Keyset Pagination
@app.get("/items/keyset")
async def get_items_keyset(
    last_id: Optional[int] = Query(None, description="Last item ID from previous page"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return")
):
    """Get items with keyset pagination (most efficient for large datasets)"""
    if last_id is None:
        items = items_db[:limit]
    else:
        # Find items after last_id
        items = [item for item in items_db if item.id > last_id][:limit]

    has_next = False
    if items:
        last_item_id = items[-1].id
        has_next = any(item.id > last_item_id for item in items_db)

    return {
        "items": items,
        "last_id": items[-1].id if items else None,
        "has_next": has_next,
        "count": len(items)
    }

# Pagination with Filtering and Sorting
@app.get("/items/advanced")
async def get_items_advanced(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in name"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("id", regex="^(id|name|price)$"),
    order: str = Query("asc", regex="^(asc|desc)$")
):
    """Get items with pagination, filtering, and sorting"""
    # Filter items
    filtered_items = items_db

    if search:
        filtered_items = [item for item in filtered_items if search.lower() in item.name.lower()]

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]

    # Sort items
    reverse = order == "desc"
    filtered_items = sorted(
        filtered_items,
        key=lambda x: getattr(x, sort_by),
        reverse=reverse
    )

    # Paginate
    total = len(filtered_items)
    total_pages = ceil(total / page_size) if total > 0 else 0

    start = (page - 1) * page_size
    end = start + page_size
    items = filtered_items[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "filters": {
            "search": search,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by,
            "order": order
        }
    }

# Pagination utility class
class Paginator:
    """Reusable pagination utility"""

    def __init__(self, items: List, page: int, page_size: int):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = len(items)
        self.total_pages = ceil(self.total / page_size) if self.total > 0 else 0

    def get_page_items(self) -> List:
        """Get items for current page"""
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        return self.items[start:end]

    def get_response(self) -> dict:
        """Get paginated response"""
        return {
            "items": self.get_page_items(),
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "has_next": self.page < self.total_pages,
            "has_previous": self.page > 1
        }

@app.get("/items/utility")
async def get_items_utility(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """Get items using pagination utility"""
    paginator = Paginator(items_db, page, page_size)
    return paginator.get_response()
