from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Menu
from app.schemas import MenuCreate, MenuResponse

router = APIRouter(
    prefix="/menus",
    tags=["Menu"]
)


# GET ALL MENU ITEMS
@router.get("/", response_model=list[MenuResponse])
def get_menus(
    db: Session = Depends(get_db)
):
    menus = db.query(Menu).all()

    return menus


# ADD MENU ITEM
@router.post("/", response_model=MenuResponse)
def add_menu(
    menu: MenuCreate,
    db: Session = Depends(get_db)
):
    new_menu = Menu(
        restaurant_id=menu.restaurant_id,
        food_name=menu.food_name,
        price=menu.price,
        category=menu.category
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    return new_menu


# GET MENU ITEM BY ID
@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db)
):
    menu = db.query(Menu).filter(
        Menu.menu_id == menu_id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=404,
            detail="Food item not found"
        )

    return menu