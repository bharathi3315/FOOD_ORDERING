from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Menu

router = APIRouter(
    prefix="/menus",
    tags=["Menu"]
)


@router.get("/")
def get_menus(db: Session = Depends(get_db)):
    menus = db.query(Menu).all()

    return menus


@router.post("/")
def add_menu(
    restaurant_id: int,
    food_name: str,
    price: int,
    category: str,
    db: Session = Depends(get_db)
):
    new_menu = Menu(
        restaurant_id=restaurant_id,
        food_name=food_name,
        price=price,
        category=category
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    return {
        "message": "Food added successfully",
        "menu_id": new_menu.menu_id,
        "food_name": new_menu.food_name
    }