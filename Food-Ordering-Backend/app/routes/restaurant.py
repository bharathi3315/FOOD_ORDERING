from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Restaurant
from app.schemas import RestaurantCreate, RestaurantResponse

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=RestaurantResponse)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db)
):
    new_restaurant = Restaurant(
        restaurant_name=restaurant.restaurant_name,
        location=restaurant.location,
        phone=restaurant.phone,
        rating=restaurant.rating
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant