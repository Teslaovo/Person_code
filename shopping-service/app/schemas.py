from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    stock: int = 0
    category: Optional[str] = "其他"
    is_hot: Optional[int] = 0
    sales: Optional[int] = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    is_hot: Optional[int] = None
    sales: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    category: str = "其他"
    is_hot: int = 0
    sales: int = 0
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


class OrderUpdateStatus(BaseModel):
    status: str


class OrderShip(BaseModel):
    tracking_number: Optional[str] = None
    tracking_company: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    items: List[OrderItemResponse] = []
    tracking_number: Optional[str] = None
    tracking_company: Optional[str] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class FavoriteBase(BaseModel):
    user_id: int
    product_id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    product: Optional[ProductResponse] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class MessageBase(BaseModel):
    from_user_id: int
    to_user_id: int
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    is_read: int = 0
    created_at: datetime
    from_user_nickname: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class ReviewBase(BaseModel):
    user_id: int
    product_id: int
    order_id: int
    rating: int
    content: Optional[str] = None
    images: Optional[str] = None


class ReviewCreate(BaseModel):
    product_id: int
    order_id: int
    rating: int
    content: Optional[str] = None
    images: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    content: Optional[str] = None
    images: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: int
    user_nickname: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True
