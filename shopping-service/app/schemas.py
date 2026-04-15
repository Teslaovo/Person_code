from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    stock: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class CartItemBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: Optional[ProductResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    total_price: float
    status: str = "pending"
    address_name: Optional[str] = None
    address_phone: Optional[str] = None
    address_province: Optional[str] = None
    address_city: Optional[str] = None
    address_district: Optional[str] = None
    address_detail: Optional[str] = None


class OrderCreate(BaseModel):
    user_id: int
    items: List[CartItemCreate]
    address_name: Optional[str] = None
    address_phone: Optional[str] = None
    address_province: Optional[str] = None
    address_city: Optional[str] = None
    address_district: Optional[str] = None
    address_detail: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True
