"""Comprehensive Error Handling"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError, validator
from typing import Any, Dict
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom Exception Classes
class CustomException(Exception):
    """Base custom exception"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ItemNotFoundException(CustomException):
    """Item not found exception"""

    def __init__(self, item_id: str):
        super().__init__(
            message=f"Item with id {item_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class InsufficientPermissionsException(CustomException):
    """Insufficient permissions exception"""

    def __init__(self):
        super().__init__(
            message="You don't have permission to perform this action",
            status_code=status.HTTP_403_FORBIDDEN
        )

class InvalidOperationException(CustomException):
    """Invalid operation exception"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class DatabaseException(CustomException):
    """Database operation exception"""

    def __init__(self, message: str):
        super().__init__(
            message=f"Database error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Error Response Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    status_code: int
    path: str
    timestamp: str

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str
    message: str
    details: list
    status_code: int

# Exception Handlers
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions"""
    logger.error(f"Custom exception: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": errors,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "path": str(request.url.path)
        }
    )

# Models with validation
class CreateUserRequest(BaseModel):
    username: str
    email: str
    age: int

    @validator("username")
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    @validator("email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @validator("age")
    def age_must_be_valid(cls, v):
        if v < 18:
            raise ValueError("Age must be at least 18")
        if v > 120:
            raise ValueError("Age must be less than 120")
        return v

# Test Endpoints
@app.get("/")
async def root():
    return {"message": "Error handling demo"}

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    """Endpoint that raises ItemNotFoundException"""
    # Simulate item lookup
    if item_id != "existing-item":
        raise ItemNotFoundException(item_id)

    return {"id": item_id, "name": "Example Item"}

@app.get("/protected")
async def protected_resource():
    """Endpoint that raises permission error"""
    # Simulate permission check
    user_has_permission = False

    if not user_has_permission:
        raise InsufficientPermissionsException()

    return {"message": "Access granted"}

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest):
    """Endpoint with validation"""
    return {
        "message": "User created successfully",
        "user": user.model_dump()
    }

@app.get("/divide/{a}/{b}")
async def divide(a: int, b: int):
    """Endpoint that can raise ZeroDivisionError"""
    try:
        result = a / b
        return {"result": result}
    except ZeroDivisionError:
        raise InvalidOperationException("Cannot divide by zero")

@app.get("/database-error")
async def database_error():
    """Endpoint that simulates database error"""
    raise DatabaseException("Connection timeout")

@app.get("/http-error")
async def http_error():
    """Endpoint that raises standard HTTPException"""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Service temporarily unavailable",
        headers={"Retry-After": "60"}
    )

@app.get("/unhandled-error")
async def unhandled_error():
    """Endpoint that raises unhandled exception"""
    # This will be caught by the general exception handler
    raise ValueError("This is an unhandled error")

# Error utility functions
def handle_database_errors(func):
    """Decorator to handle database errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise DatabaseException(str(e))

    return wrapper

@app.get("/database-operation")
@handle_database_errors
async def database_operation():
    """Endpoint with database error handling"""
    # Simulate database operation
    raise Exception("Database connection failed")
