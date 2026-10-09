
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Order, OrderItem, Menu

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# CREATE ORDER WITH FOOD ITEMS
@router.post("/")
def create_order(
    customer_id: int,
    restaurant_id: int,
    total_amount: int,
    items: list = Body(...),
    db: Session = Depends(get_db)
):
    if not items:
        raise HTTPException(
            status_code=400,
            detail="Order items are required"
        )

    calculated_total = 0
    validated_items = []

    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=400,
                detail="Each item must contain menu_id and quantity"
            )

        menu_id = item.get("menu_id")
        quantity = item.get("quantity")

        if (
            not isinstance(menu_id, int)
            or isinstance(menu_id, bool)
            or not isinstance(quantity, int)
            or isinstance(quantity, bool)
        ):
            raise HTTPException(
                status_code=400,
                detail="menu_id and quantity must be integers"
            )

        if quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than zero"
            )

        menu = db.query(Menu).filter(
            Menu.menu_id == menu_id,
            Menu.restaurant_id == restaurant_id
        ).first()

        if not menu:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item {menu_id} not found in this restaurant"
            )

        calculated_total += menu.price * quantity

        validated_items.append({
            "menu_id": menu.menu_id,
            "quantity": quantity,
            "price": menu.price
        })

    if calculated_total != total_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Total mismatch. Correct total is {calculated_total}"
        )

    try:
        new_order = Order(
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            total_amount=calculated_total,
            status="Pending"
        )

        db.add(new_order)
        db.flush()

        for item in validated_items:
            order_item = OrderItem(
                order_id=new_order.order_id,
                menu_id=item["menu_id"],
                quantity=item["quantity"],
                price=item["price"]
            )
            db.add(order_item)

        db.commit()
        db.refresh(new_order)

        return {
            "message": "Order placed successfully",
            "order_id": new_order.order_id,
            "customer_id": new_order.customer_id,
            "restaurant_id": new_order.restaurant_id,
            "status": new_order.status,
            "total_amount": new_order.total_amount,
            "items": validated_items
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save the order"
        )


# GET ALL ORDERS
@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()

    return [
        {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "restaurant_id": order.restaurant_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at
        }
        for order in orders
    ]


# GET ORDER BY ID WITH FOOD ITEMS
@router.get("/{order_id}")
def get_order(
    order_id: int,
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

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()

    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "restaurant_id": order.restaurant_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": [
            {
                "menu_id": item.menu_id,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in items
        ]
    }


# ACCEPT ORDER WITHIN 10 MINUTES
@router.put("/{order_id}/accept")
def accept_order(
    order_id: int,
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

    if order.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot accept an order with status {order.status}"
        )

    time_difference = datetime.utcnow() - order.created_at

    if time_difference > timedelta(minutes=10):
        raise HTTPException(
            status_code=400,
            detail="Order acceptance time has expired"
        )

    order.status = "Accepted"
    db.commit()
    db.refresh(order)

    return {
        "message": "Order accepted successfully",
        "order_id": order.order_id,
        "status": order.status
    }


# CANCEL ORDER WITHIN 10 MINUTES
@router.put("/{order_id}/cancel")
def cancel_order(
    order_id: int,
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

    if order.status not in ("Pending", "Accepted"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel an order with status {order.status}"
        )

    time_difference = datetime.utcnow() - order.created_at

    if time_difference > timedelta(minutes=10):
        raise HTTPException(
            status_code=400,
            detail="Order cancellation time has expired"
        )

    order.status = "Cancelled"
    db.commit()
    db.refresh(order)

    return {
        "message": "Order cancelled successfully",
        "order_id": order.order_id,
        "status": order.status
    }