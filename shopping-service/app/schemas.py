from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    images: Optional[str] = None
    stock: int = 0
    low_stock_threshold: Optional[int] = 10
    category: Optional[str] = "其他"
    is_hot: Optional[int] = 0
    is_active: Optional[int] = 1
    sales: Optional[int] = 0
    has_sku: Optional[int] = 0
    tags: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    category: Optional[str] = None
    is_hot: Optional[int] = None
    is_active: Optional[int] = None
    sales: Optional[int] = None
    tags: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    category: str = "其他"
    is_hot: int = 0
    is_active: int = 1
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
    total_price: Optional[float] = None


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
    user_id: int
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


class ProductSpecBase(BaseModel):
    product_id: int
    spec_name: str
    spec_values: str


class ProductSpecCreate(BaseModel):
    spec_name: str
    spec_values: str


class ProductSpecUpdate(BaseModel):
    spec_name: Optional[str] = None
    spec_values: Optional[str] = None


class ProductSpecResponse(ProductSpecBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class ProductSKUBase(BaseModel):
    product_id: int
    sku_name: str
    spec_json: str
    price: float
    stock: int = 0
    image: Optional[str] = None
    sales: int = 0


class ProductSKUCreate(BaseModel):
    sku_name: str
    spec_json: str
    price: float
    stock: int = 0
    image: Optional[str] = None


class ProductSKUUpdate(BaseModel):
    sku_name: Optional[str] = None
    spec_json: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image: Optional[str] = None


class ProductSKUResponse(ProductSKUBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class ProductWithSKUResponse(ProductResponse):
    specs: List[ProductSpecResponse] = []
    skus: List[ProductSKUResponse] = []

    class Config:
        orm_mode = True
        from_attributes = True


class CouponBase(BaseModel):
    name: str
    type: str = "fixed"
    value: float
    min_amount: float = 0
    total_count: int = 0
    per_limit: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    category: Optional[str] = None
    product_ids: Optional[str] = None


class CouponCreate(BaseModel):
    name: str
    type: str = "fixed"
    value: float
    min_amount: float = 0
    total_count: int = 0
    per_limit: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    category: Optional[str] = None
    product_ids: Optional[str] = None


class CouponUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[float] = None
    min_amount: Optional[float] = None
    status: Optional[str] = None


class CouponResponse(CouponBase):
    id: int
    used_count: int = 0
    status: str = "active"
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class UserCouponBase(BaseModel):
    user_id: int
    coupon_id: int


class UserCouponCreate(BaseModel):
    coupon_id: int


class UserCouponResponse(UserCouponBase):
    id: int
    status: str = "unused"
    order_id: Optional[int] = None
    received_at: datetime
    used_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class AfterSaleBase(BaseModel):
    user_id: int
    order_id: int
    order_item_id: Optional[int] = None
    type: str
    reason: str
    description: Optional[str] = None
    images: Optional[str] = None
    refund_amount: Optional[float] = None


class AfterSaleCreate(BaseModel):
    order_id: int
    order_item_id: Optional[int] = None
    type: str
    reason: str
    description: Optional[str] = None
    images: Optional[str] = None
    refund_amount: Optional[float] = None


class AfterSaleUpdate(BaseModel):
    status: Optional[str] = None
    reject_reason: Optional[str] = None


class AfterSaleResponse(AfterSaleBase):
    id: int
    status: str = "pending"
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    reject_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class SearchHistoryBase(BaseModel):
    user_id: Optional[int] = None
    keyword: str


class SearchHistoryCreate(SearchHistoryBase):
    pass


class SearchHistoryResponse(SearchHistoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class HotSearchBase(BaseModel):
    keyword: str
    search_count: Optional[int] = 0
    is_active: Optional[int] = 1
    sort_order: Optional[int] = 0


class HotSearchCreate(HotSearchBase):
    pass


class HotSearchUpdate(BaseModel):
    keyword: Optional[str] = None
    search_count: Optional[int] = None
    is_active: Optional[int] = None
    sort_order: Optional[int] = None


class HotSearchResponse(HotSearchBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class StockAlertBase(BaseModel):
    product_id: int
    sku_id: Optional[int] = None
    alert_type: str = "low_stock"
    stock_before: Optional[int] = None
    stock_after: Optional[int] = None


class StockAlertCreate(StockAlertBase):
    pass


class StockAlertUpdate(BaseModel):
    is_resolved: Optional[int] = None


class StockAlertResponse(StockAlertBase):
    id: int
    is_resolved: int = 0
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class PromotionBase(BaseModel):
    name: str
    type: str
    status: Optional[str] = "active"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Optional[str] = None
    product_ids: Optional[str] = None
    category: Optional[str] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    config: Optional[str] = None
    product_ids: Optional[str] = None
    category: Optional[str] = None


class PromotionResponse(PromotionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class ProductRecommendationBase(BaseModel):
    product_id: int
    recommended_product_id: int
    type: Optional[str] = "frequently_bought_together"
    weight: Optional[int] = 0


class ProductRecommendationCreate(ProductRecommendationBase):
    pass


class ProductRecommendationUpdate(BaseModel):
    weight: Optional[int] = None


class ProductRecommendationResponse(ProductRecommendationBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class SalesStats(BaseModel):
    period: str
    total_orders: int
    total_sales: float
    total_products: int


class ProductSalesRank(BaseModel):
    product_id: int
    product_name: str
    sales_count: int
    sales_amount: float


class UserGrowthStats(BaseModel):
    date: str
    new_users: int
    total_users: int


class OrderConversionStats(BaseModel):
    total_visits: int
    cart_adds: int
    orders_created: int
    orders_paid: int
    conversion_rate: float
