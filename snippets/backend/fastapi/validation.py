"""Advanced Validation Patterns"""
from fastapi import FastAPI, HTTPException, status, Query, Path, Body
from pydantic import BaseModel, Field, validator, root_validator, EmailStr, HttpUrl, constr, confloat
from typing import Optional, List
from datetime import datetime, date
import re

app = FastAPI()

# Basic validation models
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: constr(min_length=8, max_length=100)
    age: int = Field(..., ge=18, le=120, description="Age must be between 18 and 120")
    website: Optional[HttpUrl] = None

    @validator("password")
    def password_strength(cls, v):
        """Validate password strength"""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @validator("username")
    def username_no_spaces(cls, v):
        """Validate username has no spaces"""
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        return v

# Advanced validation
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: confloat(gt=0, le=1000000)
    discount_price: Optional[confloat(gt=0)] = None
    stock: int = Field(..., ge=0)
    category: str
    tags: List[str] = Field(default_factory=list, max_items=10)

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags"""
        if len(v) != len(set(v)):
            raise ValueError("Tags must be unique")
        return v

    @root_validator
    def check_discount_price(cls, values):
        """Validate discount price is less than regular price"""
        price = values.get("price")
        discount_price = values.get("discount_price")

        if discount_price and price and discount_price >= price:
            raise ValueError("Discount price must be less than regular price")

        return values

# Date and time validation
class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    start_date: datetime
    end_date: datetime
    registration_deadline: Optional[date] = None

    @root_validator
    def validate_dates(cls, values):
        """Validate date relationships"""
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        registration_deadline = values.get("registration_deadline")

        if start_date and end_date and start_date >= end_date:
            raise ValueError("End date must be after start date")

        if registration_deadline and start_date:
            if registration_deadline >= start_date.date():
                raise ValueError("Registration deadline must be before start date")

        return values

# Conditional validation
class PaymentCreate(BaseModel):
    amount: confloat(gt=0)
    payment_method: str = Field(..., regex="^(credit_card|debit_card|paypal|bank_transfer)$")
    card_number: Optional[str] = None
    card_cvv: Optional[str] = None
    paypal_email: Optional[EmailStr] = None
    bank_account: Optional[str] = None

    @root_validator
    def validate_payment_details(cls, values):
        """Validate payment details based on payment method"""
        payment_method = values.get("payment_method")

        if payment_method in ["credit_card", "debit_card"]:
            if not values.get("card_number"):
                raise ValueError("Card number is required for card payments")
            if not values.get("card_cvv"):
                raise ValueError("CVV is required for card payments")

        elif payment_method == "paypal":
            if not values.get("paypal_email"):
                raise ValueError("PayPal email is required for PayPal payments")

        elif payment_method == "bank_transfer":
            if not values.get("bank_account"):
                raise ValueError("Bank account is required for bank transfers")

        return values

# Custom validators
def validate_phone_number(phone: str) -> str:
    """Custom phone number validator"""
    # Remove spaces and dashes
    cleaned = re.sub(r"[\s\-]", "", phone)

    # Check if it's a valid format (simple example)
    if not re.match(r"^\+?1?\d{10,15}$", cleaned):
        raise ValueError("Invalid phone number format")

    return cleaned

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=1000)

    @validator("phone")
    def validate_phone(cls, v):
        return validate_phone_number(v)

# Query parameter validation
@app.get("/search")
async def search(
    q: str = Query(..., min_length=3, max_length=100, description="Search query"),
    page: int = Query(1, ge=1, le=1000, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|name|price)$"),
    order: str = Query("asc", regex="^(asc|desc)$")
):
    """Search with validated query parameters"""
    return {
        "query": q,
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "order": order
    }

# Path parameter validation
@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(..., ge=1, le=999999, description="Item ID")
):
    """Get item with validated path parameter"""
    return {"item_id": item_id}

# Body validation
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate = Body(..., example={
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "age": 25
    })
):
    """Create user with validated body"""
    return {"message": "User created successfully", "username": user.username}

@app.post("/products/", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """Create product with advanced validation"""
    return {"message": "Product created successfully", "name": product.name}

@app.post("/events/", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """Create event with date validation"""
    return {"message": "Event created successfully", "title": event.title}

@app.post("/payments/", status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate):
    """Create payment with conditional validation"""
    return {
        "message": "Payment processed successfully",
        "amount": payment.amount,
        "method": payment.payment_method
    }

@app.post("/contacts/", status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate):
    """Create contact with custom validation"""
    return {"message": "Contact created successfully", "name": contact.name}

# Validation with dependencies
def validate_api_key(api_key: str = Query(..., min_length=32, max_length=32)):
    """Validate API key"""
    # In production, check against database
    if api_key != "a" * 32:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

@app.get("/protected")
async def protected_endpoint(api_key: str = Depends(validate_api_key)):
    """Protected endpoint with API key validation"""
    return {"message": "Access granted"}
