from fastapi import FastAPI

from app.database import Base, engine
from app import models

from app.routes import customer, restaurant, menu, order, order_item
from app.routes import customer, restaurant, menu, order, order_item, delivery
from app.routes import customer, restaurant, menu, order, order_item, delivery, payment
from app.routes import customer, restaurant, menu, order, order_item, delivery, payment, recommendation
app = FastAPI(
    title="Food Ordering and Delivery Platform"
)

Base.metadata.create_all(bind=engine)

app.include_router(customer.router)
app.include_router(restaurant.router)
app.include_router(menu.router)
app.include_router(order.router)
app.include_router(order_item.router)
app.include_router(delivery.router)
app.include_router(payment.router)
app.include_router(recommendation.router)


@app.get("/")
def home():
    return {
        "message": "Backend is running"
    }