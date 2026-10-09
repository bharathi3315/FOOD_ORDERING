from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Payment

router = APIRouter(
    prefix="/payments",
    tags=["Payment"]
)


# CREATE PAYMENT
@router.post("/")
def create_payment(
    order_id: int,
    payment_method: str,
    amount: int,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    new_payment = Payment(
        order_id=order_id,
        payment_method=payment_method,
        amount=amount,
        payment_status="Paid",
        transaction_id=transaction_id
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {
        "message": "Payment successful",
        "payment_id": new_payment.payment_id,
        "status": new_payment.payment_status
    }


# GET ALL PAYMENTS
@router.get("/")
def get_payments(
    db: Session = Depends(get_db)
):
    payments = db.query(Payment).all()

    return payments


# GET PAYMENT BY ID
@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(
        Payment.payment_id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment