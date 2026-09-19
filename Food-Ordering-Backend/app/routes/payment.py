from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Payment, Order

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/")
def create_payment(
    order_id: int,
    payment_method: str,
    amount: int,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.order_id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

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
        "order_id": new_payment.order_id,
        "payment_method": new_payment.payment_method,
        "amount": new_payment.amount,
        "payment_status": new_payment.payment_status,
        "transaction_id": new_payment.transaction_id
    }