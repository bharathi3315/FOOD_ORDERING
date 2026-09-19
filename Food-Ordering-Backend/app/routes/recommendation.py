from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recommendation, Customer, Menu

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


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
@router.get("/{customer_id}")
def get_recommendations(
    customer_id: int,
    db: Session = Depends(get_db)
):
    recommendations = db.query(
        Recommendation, Menu
    ).join(
        Menu,
        Recommendation.menu_id == Menu.menu_id
    ).filter(
        Recommendation.customer_id == customer_id
    ).all()

    result = []

    for recommendation, menu in recommendations:
        result.append({
            "menu_id": menu.menu_id,
            "food_name": menu.food_name,
            "price": menu.price,
            "category": menu.category,
            "score": recommendation.score
        })

    return result