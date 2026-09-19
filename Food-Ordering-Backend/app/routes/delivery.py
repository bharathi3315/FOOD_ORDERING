from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Delivery, Order


router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"]
)


# ---------------- CREATE DELIVERY ----------------

@router.post("/")
def create_delivery(
    order_id: int,
    delivery_partner_name: str,
    phone: str,
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

    new_delivery = Delivery(
        order_id=order_id,
        delivery_partner_name=delivery_partner_name,
        phone=phone,
        status="Assigned"
    )

    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)

    return {
        "message": "Delivery assigned successfully",
        "delivery_id": new_delivery.delivery_id,
        "order_id": new_delivery.order_id,
        "delivery_partner_name": new_delivery.delivery_partner_name,
        "phone": new_delivery.phone,
        "status": new_delivery.status
    }


# ---------------- GET DELIVERY ----------------

@router.get("/{delivery_id}")
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db)
):

    delivery = db.query(Delivery).filter(
        Delivery.delivery_id == delivery_id
    ).first()

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    return {
        "delivery_id": delivery.delivery_id,
        "order_id": delivery.order_id,
        "delivery_partner_name": delivery.delivery_partner_name,
        "phone": delivery.phone,
        "status": delivery.status
    }


# ---------------- UPDATE DELIVERY STATUS ----------------

@router.put("/{delivery_id}/status")
def update_delivery_status(
    delivery_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    delivery = db.query(Delivery).filter(
        Delivery.delivery_id == delivery_id
    ).first()

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    delivery.status = status

    db.commit()
    db.refresh(delivery)

    return {
        "message": "Delivery status updated successfully",
        "delivery_id": delivery.delivery_id,
        "status": delivery.status
    }