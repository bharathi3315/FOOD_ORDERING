from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Order,
    Customer,
    Restaurant,
    OrderItem,
    Menu
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ---------------- GET ALL ORDERS ----------------

@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders


# ---------------- CREATE ORDER ----------------

@router.post("/")
def create_order(
    customer_id: int,
    restaurant_id: int,
    menu_id: int,
    quantity: int,
    total_amount: int,
    db: Session = Depends(get_db)
):

    # Check customer
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Check restaurant
    restaurant = db.query(Restaurant).filter(
        Restaurant.restaurant_id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    # Check menu
    menu = db.query(Menu).filter(
        Menu.menu_id == menu_id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    # Create order
    new_order = Order(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        total_amount=total_amount,
        status="Pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Create order item
    new_order_item = OrderItem(
        order_id=new_order.order_id,
        menu_id=menu_id,
        quantity=quantity,
        price=menu.price
    )

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    return {
        "message": "Order created successfully",
        "order_id": new_order.order_id,
        "customer_id": new_order.customer_id,
        "restaurant_id": new_order.restaurant_id,
        "menu_id": menu_id,
        "food_name": menu.food_name,
        "quantity": quantity,
        "total_amount": new_order.total_amount,
        "status": new_order.status
    }


# ---------------- CUSTOMER ORDERS ----------------

@router.get("/customer/{customer_id}")
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(
        Order.customer_id == customer_id
    ).all()

    return orders


# ---------------- ORDER HISTORY ----------------

@router.get("/customer/{customer_id}/history")
def get_order_history(
    customer_id: int,
    db: Session = Depends(get_db)
):

    history = (
        db.query(Order, OrderItem, Menu)
        .join(
            OrderItem,
            Order.order_id == OrderItem.order_id
        )
        .join(
            Menu,
            OrderItem.menu_id == Menu.menu_id
        )
        .filter(
            Order.customer_id == customer_id
        )
        .all()
    )

    result = []

    for order, item, menu in history:

        result.append({
            "order_id": order.order_id,
            "food_name": menu.food_name,
            "quantity": item.quantity,
            "price": item.price,
            "status": order.status
        })

    return result