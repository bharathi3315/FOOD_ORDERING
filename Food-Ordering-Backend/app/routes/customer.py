from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer

router = APIRouter(
    prefix="/customers",
    tags=["Customer"]
)


# Register Customer
@router.post("/register")
def register_customer(
    name: str,
    email: str,
    phone: str,
    address: str,
    password: str,
    db: Session = Depends(get_db)
):
    existing_customer = db.query(Customer).filter(
        Customer.email == email
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    customer = Customer(
        name=name,
        email=email,
        phone=phone,
        address=address,
        password=password
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {
        "message": "Customer registered successfully",
        "customer_id": customer.customer_id
    }


# Login Customer
@router.post("/login")
def login_customer(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.email == email
    ).first()

    if not customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if customer.password != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email
    }