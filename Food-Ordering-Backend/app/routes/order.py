from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, Customer, Restaurant
from app.models import Order, Customer, Restaurant, OrderItem, Menu

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders


@router.post("/")
def create_order(
    customer_id: int,
    restaurant_id: int,
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

    return {
        "message": "Order created successfully",
        "order_id": new_order.order_id,
        "customer_id": new_order.customer_id,
        "restaurant_id": new_order.restaurant_id,
        "total_amount": new_order.total_amount,
        "status": new_order.status
    }
@router.get("/customer/{customer_id}")
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(
        Order.customer_id == customer_id
    ).all()

    return orders
@router.get("/customer/{customer_id}/history")
def get_order_history(
    customer_id: int,
    db: Session = Depends(get_db)
):
    history = (
        db.query(Order, OrderItem, Menu)
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .join(Menu, OrderItem.menu_id == Menu.menu_id)
        .filter(Order.customer_id == customer_id)
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