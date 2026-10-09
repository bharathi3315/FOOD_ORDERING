from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recommendation

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendation"]
)


# ADD RECOMMENDATION
@router.post("/")
def add_recommendation(
    customer_id: int,
    menu_id: int,
    score: int,
    db: Session = Depends(get_db)
):
    new_recommendation = Recommendation(
        customer_id=customer_id,
        menu_id=menu_id,
        score=score
    )

    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)

    return {
        "message": "Recommendation added successfully",
        "recommendation_id": new_recommendation.recommendation_id
    }


# GET CUSTOMER RECOMMENDATIONS
@router.get("/{customer_id}")
def get_recommendations(
    customer_id: int,
    db: Session = Depends(get_db)
):
    recommendations = db.query(Recommendation).filter(
        Recommendation.customer_id == customer_id
    ).order_by(
        Recommendation.score.desc()
    ).all()

    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found"
        )

    return recommendations