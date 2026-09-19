from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OrderItem, Order, Menu

router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


@router.post("/")
def create_order_item(
    order_id: int,
    menu_id: int,
    quantity: int,
    price: int,
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

    menu = db.query(Menu).filter(
        Menu.menu_id == menu_id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    new_item = OrderItem(
        order_id=order_id,
        menu_id=menu_id,
        quantity=quantity,
        price=price
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {
        "message": "Order item added successfully",
        "order_item_id": new_item.order_item_id,
        "order_id": new_item.order_id,
        "menu_id": new_item.menu_id,
        "quantity": new_item.quantity,
        "price": new_item.price
    }