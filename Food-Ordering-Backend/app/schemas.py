from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    password: str


class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: str
    address: str

    class Config:
        from_attributes = True


class CustomerLogin(BaseModel):
    email: str
    password: str
class RestaurantCreate(BaseModel):
    restaurant_name: str
    location: str
    phone: str
    rating: str


class RestaurantResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    location: str
    phone: str
    rating: str

    class Config:
        from_attributes = True