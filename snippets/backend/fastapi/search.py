"""Search and Filtering Implementation"""
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# Models
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    tags: List[str]
    in_stock: bool
    created_at: datetime

# Sample data
products = [
    Product(
        id=i,
        name=f"Product {i}",
        description=f"Description for product {i}",
        price=10.0 + i * 5,
        category=["Electronics", "Books", "Clothing", "Home"][i % 4],
        tags=["sale", "new", "featured"][:i % 3],
        in_stock=i % 2 == 0,
        created_at=datetime.utcnow()
    )
    for i in range(1, 51)
]

# Full-text search
def full_text_search(items: List[Product], query: str) -> List[Product]:
    """Simple full-text search"""
    query_lower = query.lower()
    return [
        item for item in items
        if query_lower in item.name.lower()
        or query_lower in item.description.lower()
    ]

# Filtering
def filter_products(
    products: List[Product],
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    tags: Optional[List[str]] = None
) -> List[Product]:
    """Filter products by multiple criteria"""
    filtered = products

    if category:
        filtered = [p for p in filtered if p.category == category]

    if min_price is not None:
        filtered = [p for p in filtered if p.price >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p.price <= max_price]

    if in_stock is not None:
        filtered = [p for p in filtered if p.in_stock == in_stock]

    if tags:
        filtered = [
            p for p in filtered
            if any(tag in p.tags for tag in tags)
        ]

    return filtered

# Sorting
def sort_products(
    products: List[Product],
    sort_by: str = "id",
    order: str = "asc"
) -> List[Product]:
    """Sort products"""
    reverse = order == "desc"

    if sort_by == "price":
        return sorted(products, key=lambda x: x.price, reverse=reverse)
    elif sort_by == "name":
        return sorted(products, key=lambda x: x.name, reverse=reverse)
    elif sort_by == "created_at":
        return sorted(products, key=lambda x: x.created_at, reverse=reverse)
    else:
        return sorted(products, key=lambda x: x.id, reverse=reverse)

# Endpoints
@app.get("/search", response_model=List[Product])
async def search_products(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort_by: str = Query("id", regex="^(id|name|price|created_at)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Search and filter products"""
    result = products

    # Apply search
    if q:
        result = full_text_search(result, q)

    # Apply filters
    result = filter_products(
        result,
        category=category,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        tags=tags
    )

    # Apply sorting
    result = sort_products(result, sort_by=sort_by, order=order)

    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    return paginated

@app.get("/products/faceted-search")
async def faceted_search(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Faceted search with aggregations"""
    filtered = filter_products(
        products,
        category=category,
        min_price=min_price,
        max_price=max_price
    )

    # Calculate facets
    categories = {}
    price_ranges = {"0-50": 0, "50-100": 0, "100+": 0}
    stock_status = {"in_stock": 0, "out_of_stock": 0}

    for product in products:
        # Category facet
        categories[product.category] = categories.get(product.category, 0) + 1

        # Price range facet
        if product.price < 50:
            price_ranges["0-50"] += 1
        elif product.price < 100:
            price_ranges["50-100"] += 1
        else:
            price_ranges["100+"] += 1

        # Stock status facet
        if product.in_stock:
            stock_status["in_stock"] += 1
        else:
            stock_status["out_of_stock"] += 1

    return {
        "results": filtered,
        "facets": {
            "categories": categories,
            "price_ranges": price_ranges,
            "stock_status": stock_status
        },
        "total": len(filtered)
    }
