from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    address = Column(String(255))
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String(150), nullable=False)
    location = Column(String(255))
    phone = Column(String(15))
    rating = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)


class Menu(Base):
    __tablename__ = "menus"

    menu_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    food_name = Column(String(150), nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    total_amount = Column(Integer, nullable=False)
    status = Column(String(50), default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    menu_id = Column(Integer, ForeignKey("menus.menu_id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
class Delivery(Base):
    __tablename__ = "deliveries"

    delivery_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    delivery_partner_name = Column(String(100), nullable=False)
    phone = Column(String(15))
    status = Column(String(50), default="Assigned")
    assigned_time = Column(DateTime, default=datetime.utcnow)
    delivered_time = Column(DateTime, nullable=True)
class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    payment_method = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    payment_status = Column(String(50), default="Pending")
    payment_date = Column(DateTime, default=datetime.utcnow)
    transaction_id = Column(String(100), unique=True)
class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    menu_id = Column(Integer, ForeignKey("menus.menu_id"))
    score = Column(Integer, default=0)
    suggested_on = Column(DateTime, default=datetime.utcnow)