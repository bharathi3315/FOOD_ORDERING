from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OrderItem

router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


# ADD ORDER ITEM
@router.post("/")
def add_order_item(
    order_id: int,
    menu_id: int,
    quantity: int,
    price: int,
    db: Session = Depends(get_db)
):
    new_order_item = OrderItem(
        order_id=order_id,
        menu_id=menu_id,
        quantity=quantity,
        price=price
    )

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    return {
        "message": "Order item added successfully",
        "order_item_id": new_order_item.order_item_id
    }


# GET ALL ORDER ITEMS
@router.get("/")
def get_order_items(
    db: Session = Depends(get_db)
):
    order_items = db.query(OrderItem).all()

    return order_items


# GET ORDER ITEM BY ID
@router.get("/{order_item_id}")
def get_order_item(
    order_item_id: int,
    db: Session = Depends(get_db)
):
    order_item = db.query(OrderItem).filter(
        OrderItem.order_item_id == order_item_id
    ).first()

    if not order_item:
        raise HTTPException(
            status_code=404,
            detail="Order item not found"
        )

    return order_item