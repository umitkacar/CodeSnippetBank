"""Payment Integration"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from enum import Enum

app = FastAPI()

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    payment_method: str
    customer_id: str
    description: Optional[str] = None

class Payment(BaseModel):
    id: str
    amount: float
    currency: str
    status: PaymentStatus
    customer_id: str

payments_db = {}

@app.post("/payments/", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_request: PaymentRequest):
    """Create a payment"""
    # In production, integrate with Stripe/PayPal/etc
    payment_id = f"pay_{len(payments_db) + 1}"

    payment = Payment(
        id=payment_id,
        amount=payment_request.amount,
        currency=payment_request.currency,
        status=PaymentStatus.PENDING,
        customer_id=payment_request.customer_id
    )

    payments_db[payment_id] = payment

    # Simulate payment processing
    payment.status = PaymentStatus.COMPLETED

    return payment

@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Get payment by ID"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payments_db[payment_id]

@app.post("/payments/{payment_id}/refund")
async def refund_payment(payment_id: str):
    """Refund a payment"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payments_db[payment_id]
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Payment cannot be refunded")

    payment.status = PaymentStatus.REFUNDED
    return payment
