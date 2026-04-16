from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)  # 默认价格（SKU 价格优先级更高）
    image = Column(String)
    images = Column(String)  # JSON 数组存储多张图片
    stock = Column(Integer, default=0)  # 总库存（所有 SKU 库存之和）
    category = Column(String, default="其他")  # 商品分类
    is_hot = Column(Integer, default=0)  # 是否热门 0-否 1-是
    sales = Column(Integer, default=0)  # 销量
    has_sku = Column(Integer, default=0)  # 是否有规格 0-否 1-是
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    skus = relationship("ProductSKU", back_populates="product", cascade="all, delete-orphan")
    specs = relationship("ProductSpec", back_populates="product", cascade="all, delete-orphan")


class ProductSpec(Base):
    __tablename__ = "product_specs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    spec_name = Column(String, nullable=False)  # 规格名称，如"颜色"、"尺寸"
    spec_values = Column(String, nullable=False)  # JSON 数组存储规格值，如["红色","蓝色"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="specs")


class ProductSKU(Base):
    __tablename__ = "product_skus"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku_name = Column(String, nullable=False)  # SKU 名称，如"红色+XL"
    spec_json = Column(String, nullable=False)  # JSON 存储规格键值对，如{"颜色":"红色","尺寸":"XL"}
    price = Column(Float, nullable=False)  # SKU 价格
    stock = Column(Integer, default=0)  # SKU 库存
    image = Column(String)  # SKU 图片
    sales = Column(Integer, default=0)  # SKU 销量
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="skus")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending(待付款), paid(待发货), shipped(待收货), completed(已完成), cancelled(已取消)
    # 收货地址信息（快照）
    address_name = Column(String)
    address_phone = Column(String)
    address_province = Column(String)
    address_city = Column(String)
    address_district = Column(String)
    address_detail = Column(String)
    # 物流信息
    tracking_number = Column(String)  # 物流单号
    tracking_company = Column(String)  # 物流公司
    # 时间节点
    paid_at = Column(DateTime(timezone=True))  # 付款时间
    shipped_at = Column(DateTime(timezone=True))  # 发货时间
    completed_at = Column(DateTime(timezone=True))  # 完成时间
    cancelled_at = Column(DateTime(timezone=True))  # 取消时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="items")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_user_id = Column(Integer, nullable=False)
    to_user_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Integer, default=0)  # 0-未读 1-已读
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 星
    content = Column(String)
    images = Column(String)  # JSON 数组存储图片URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)  # 优惠券名称
    type = Column(String, default="fixed")  # fixed-固定金额 discount-折扣
    value = Column(Float, nullable=False)  # 优惠值（金额或折扣率）
    min_amount = Column(Float, default=0)  # 最低使用门槛
    total_count = Column(Integer, default=0)  # 发放总数
    used_count = Column(Integer, default=0)  # 已使用数量
    per_limit = Column(Integer, default=1)  # 每人限领数量
    start_time = Column(DateTime(timezone=True))  # 开始时间
    end_time = Column(DateTime(timezone=True))  # 结束时间
    status = Column(String, default="active")  # active-活动中 inactive-已结束
    category = Column(String)  # 限定分类（空表示不限）
    product_ids = Column(String)  # JSON 数组，限定商品（空表示不限）
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserCoupon(Base):
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    status = Column(String, default="unused")  # unused-未使用 used-已使用 expired-已过期
    order_id = Column(Integer)  # 使用的订单ID
    received_at = Column(DateTime(timezone=True), server_default=func.now())  # 领取时间
    used_at = Column(DateTime(timezone=True))  # 使用时间


class AfterSale(Base):
    __tablename__ = "after_sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"))  # 可针对单项或整单
    type = Column(String, nullable=False)  # refund-仅退款 return-退货退款 exchange-换货
    reason = Column(String, nullable=False)  # 售后原因
    description = Column(String)  # 详细描述
    images = Column(String)  # JSON 数组，凭证图片
    refund_amount = Column(Float)  # 退款金额
    status = Column(String, default="pending")  # pending-待审核 approved-已审核 rejected-已拒绝 processing-处理中 completed-已完成
    approved_at = Column(DateTime(timezone=True))  # 审核时间
    approved_by = Column(Integer)  # 审核管理员ID
    reject_reason = Column(String)  # 拒绝原因
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    sku_id = Column(Integer)  # SKU ID，可为空
    type = Column(String, nullable=False)  # in-入库 out-出库 adjust-调整 order-订单扣减 cancel-取消回滚
    change = Column(Integer, nullable=False)  # 变动数量（正为加，负为减）
    before_stock = Column(Integer, nullable=False)  # 变动前库存
    after_stock = Column(Integer, nullable=False)  # 变动后库存
    order_id = Column(Integer)  # 关联订单ID
    remark = Column(String)  # 备注
    created_at = Column(DateTime(timezone=True), server_default=func.now())
