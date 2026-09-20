from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Recommendation,
    Customer,
    Menu,
    Order,
    OrderItem
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


# ---------------- CREATE RECOMMENDATION ----------------

@router.post("/")
def create_recommendation(
    customer_id: int,
    menu_id: int,
    score: int,
    db: Session = Depends(get_db)
):

    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    menu = db.query(Menu).filter(
        Menu.menu_id == menu_id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    new_recommendation = Recommendation(
        customer_id=customer_id,
        menu_id=menu_id,
        score=score
    )

    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)

    return {
        "message": "Food recommendation created",
        "recommendation_id": new_recommendation.recommendation_id,
        "customer_id": new_recommendation.customer_id,
        "menu_id": new_recommendation.menu_id,
        "score": new_recommendation.score
    }


# ---------------- GET RECOMMENDATIONS ----------------

@router.get("/{customer_id}")
def get_recommendations(
    customer_id: int,
    db: Session = Depends(get_db)
):

    # Get customer's previous orders
    previous_orders = (
        db.query(OrderItem)
        .join(
            Order,
            Order.order_id == OrderItem.order_id
        )
        .filter(
            Order.customer_id == customer_id
        )
        .all()
    )

    if not previous_orders:
        return []

    # Get menu IDs already ordered
    ordered_menu_ids = [
        item.menu_id
        for item in previous_orders
    ]

    # Get previous menu items
    previous_menus = (
        db.query(Menu)
        .filter(
            Menu.menu_id.in_(ordered_menu_ids)
        )
        .all()
    )

    if not previous_menus:
        return []

    # Take category from previous food
    categories = [
        menu.category
        for menu in previous_menus
        if menu.category
    ]

    if not categories:
        return []

    # Find other foods from same category
    recommended_menus = (
        db.query(Menu)
        .filter(
            Menu.category.in_(categories),
            ~Menu.menu_id.in_(ordered_menu_ids)
        )
        .all()
    )

    result = []

    for menu in recommended_menus:

        result.append({
            "menu_id": menu.menu_id,
            "food_name": menu.food_name,
            "price": menu.price,
            "category": menu.category,
            "restaurant_id": menu.restaurant_id,
            "score": 10
        })

    return result