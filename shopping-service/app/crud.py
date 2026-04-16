from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100, category: str = None, search: str = None):
    query = db.query(models.Product)
    if category and category != "全部":
        query = query.filter(models.Product.category == category)
    if search:
        query = query.filter(
            or_(
                models.Product.name.contains(search),
                models.Product.description.contains(search)
            )
        )
    return query.offset(skip).limit(limit).all()


def get_categories(db: Session):
    products = db.query(models.Product).all()
    categories = list(set([p.category for p in products if p.category]))
    categories.sort()
    return ["全部"] + categories


def get_hot_products(db: Session, limit: int = 10):
    return db.query(models.Product).filter(
        models.Product.is_hot == 1
    ).order_by(
        models.Product.sales.desc()
    ).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return db_product


def get_cart_by_user(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()


def get_cart_item(db: Session, cart_id: int):
    return db.query(models.CartItem).filter(models.CartItem.id == cart_id).first()


def get_cart_item_by_user_and_product(db: Session, user_id: int, product_id: int):
    return db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id
    ).first()


def add_to_cart(db: Session, cart_item: schemas.CartItemCreate):
    existing = get_cart_item_by_user_and_product(db, cart_item.user_id, cart_item.product_id)
    if existing:
        existing.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing)
        return existing
    db_cart = models.CartItem(**cart_item.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def update_cart_item(db: Session, cart_id: int, quantity: int):
    db_cart = get_cart_item(db, cart_id)
    if not db_cart:
        return None
    db_cart.quantity = quantity
    db.commit()
    db.refresh(db_cart)
    return db_cart


def delete_cart_item(db: Session, cart_id: int):
    db_cart = get_cart_item(db, cart_id)
    if not db_cart:
        return None
    db.delete(db_cart)
    db.commit()
    return db_cart


def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, user_id: int, items: list, total_price: float, address_data: dict = None):
    # 先检查并扣减库存，同时增加销量
    for item in items:
        product = get_product(db, item.product_id)
        if not product:
            raise ValueError(f"商品 {item.product_id} 不存在")
        if product.stock < item.quantity:
            raise ValueError(f"商品 {product.name} 库存不足，当前库存: {product.stock}")
        product.stock -= item.quantity
        product.sales += item.quantity  # 增加销量

    db_order = models.Order(user_id=user_id, total_price=total_price, status="pending")
    if address_data:
        db_order.address_name = address_data.get("name")
        db_order.address_phone = address_data.get("phone")
        db_order.address_province = address_data.get("province")
        db_order.address_city = address_data.get("city")
        db_order.address_district = address_data.get("district")
        db_order.address_detail = address_data.get("detail")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    for item in items:
        product = get_product(db, item.product_id)
        order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price if product else 0
        )
        db.add(order_item)
    db.commit()
    return db_order


def update_order_status(db: Session, order_id: int, status: str):
    from sqlalchemy.sql import func
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    db_order.status = status
    if status == "paid":
        db_order.paid_at = func.now()
    elif status == "shipped":
        db_order.shipped_at = func.now()
    elif status == "completed":
        db_order.completed_at = func.now()
    elif status == "cancelled":
        db_order.cancelled_at = func.now()
        # 取消订单时恢复库存和销量
        for item in db_order.items:
            product = get_product(db, item.product_id)
            if product:
                product.stock += item.quantity
                product.sales -= item.quantity
    db.commit()
    db.refresh(db_order)
    return db_order


def ship_order(db: Session, order_id: int, tracking_number: str = None, tracking_company: str = None):
    from sqlalchemy.sql import func
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    if tracking_number:
        db_order.tracking_number = tracking_number
    if tracking_company:
        db_order.tracking_company = tracking_company
    db_order.status = "shipped"
    db_order.shipped_at = func.now()
    db.commit()
    db.refresh(db_order)
    return db_order


def get_favorites_by_user(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()


def get_favorite(db: Session, user_id: int, product_id: int):
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.product_id == product_id
    ).first()


def add_favorite(db: Session, favorite: schemas.FavoriteCreate):
    existing = get_favorite(db, favorite.user_id, favorite.product_id)
    if existing:
        return existing
    db_favorite = models.Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def remove_favorite(db: Session, user_id: int, product_id: int):
    db_favorite = get_favorite(db, user_id, product_id)
    if not db_favorite:
        return None
    db.delete(db_favorite)
    db.commit()
    return db_favorite


def remove_favorite_by_id(db: Session, favorite_id: int):
    db_favorite = db.query(models.Favorite).filter(models.Favorite.id == favorite_id).first()
    if not db_favorite:
        return None
    db.delete(db_favorite)
    db.commit()
    return db_favorite


def get_messages_by_user(db: Session, user_id: int, other_user_id: int = None):
    query = db.query(models.Message).filter(
        (models.Message.from_user_id == user_id) | (models.Message.to_user_id == user_id)
    )
    if other_user_id:
        query = query.filter(
            (models.Message.from_user_id == other_user_id) | (models.Message.to_user_id == other_user_id)
        )
    return query.order_by(models.Message.created_at.asc()).all()


def get_unread_count(db: Session, user_id: int):
    return db.query(models.Message).filter(
        models.Message.to_user_id == user_id,
        models.Message.is_read == 0
    ).count()


def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def mark_as_read(db: Session, message_id: int):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db_message.is_read = 1
        db.commit()
        db.refresh(db_message)
    return db_message


def mark_conversation_as_read(db: Session, user_id: int, other_user_id: int):
    db.query(models.Message).filter(
        models.Message.from_user_id == other_user_id,
        models.Message.to_user_id == user_id,
        models.Message.is_read == 0
    ).update({"is_read": 1})
    db.commit()


def get_conversation_users(db: Session, user_id: int):
    messages = db.query(models.Message).filter(
        (models.Message.from_user_id == user_id) | (models.Message.to_user_id == user_id)
    ).all()
    user_ids = set()
    for msg in messages:
        if msg.from_user_id != user_id:
            user_ids.add(msg.from_user_id)
        if msg.to_user_id != user_id:
            user_ids.add(msg.to_user_id)
    return list(user_ids)


def get_reviews_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Review).filter(models.Review.product_id == product_id).order_by(
        models.Review.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_reviews_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Review).filter(models.Review.user_id == user_id).order_by(
        models.Review.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_review(db: Session, review_id: int):
    return db.query(models.Review).filter(models.Review.id == review_id).first()


def get_review_by_order_and_product(db: Session, order_id: int, product_id: int):
    return db.query(models.Review).filter(
        models.Review.order_id == order_id,
        models.Review.product_id == product_id
    ).first()


def create_review(db: Session, user_id: int, review: schemas.ReviewCreate):
    # 检查是否已经评价过
    existing = get_review_by_order_and_product(db, review.order_id, review.product_id)
    if existing:
        raise ValueError("该商品已评价")
    db_review = models.Review(
        user_id=user_id,
        product_id=review.product_id,
        order_id=review.order_id,
        rating=review.rating,
        content=review.content,
        images=review.images
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: int, review: schemas.ReviewUpdate):
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    update_data = review.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int):
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    db.delete(db_review)
    db.commit()
    return db_review


def get_pending_review_products(db: Session, user_id: int, order_id: int):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user_id,
        models.Order.status == "completed"
    ).first()
    if not order:
        return []
    reviewed_product_ids = [r.product_id for r in db.query(models.Review).filter(
        models.Review.order_id == order_id,
        models.Review.user_id == user_id
    ).all()]
    pending_items = []
    for item in order.items:
        if item.product_id not in reviewed_product_ids:
            pending_items.append(item)
    return pending_items


def get_specs_by_product(db: Session, product_id: int):
    return db.query(models.ProductSpec).filter(models.ProductSpec.product_id == product_id).all()


def get_spec(db: Session, spec_id: int):
    return db.query(models.ProductSpec).filter(models.ProductSpec.id == spec_id).first()


def create_spec(db: Session, product_id: int, spec: schemas.ProductSpecCreate):
    db_spec = models.ProductSpec(product_id=product_id, **spec.dict())
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    db.query(models.Product).filter(models.Product.id == product_id).update({"has_sku": 1})
    db.commit()
    return db_spec


def update_spec(db: Session, spec_id: int, spec: schemas.ProductSpecUpdate):
    db_spec = get_spec(db, spec_id)
    if not db_spec:
        return None
    update_data = spec.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_spec, key, value)
    db.commit()
    db.refresh(db_spec)
    return db_spec


def delete_spec(db: Session, spec_id: int):
    db_spec = get_spec(db, spec_id)
    if not db_spec:
        return None
    db.delete(db_spec)
    db.commit()
    remaining = db.query(models.ProductSpec).filter(models.ProductSpec.product_id == db_spec.product_id).count()
    if remaining == 0:
        db.query(models.Product).filter(models.Product.id == db_spec.product_id).update({"has_sku": 0})
        db.commit()
    return db_spec


def get_skus_by_product(db: Session, product_id: int):
    return db.query(models.ProductSKU).filter(models.ProductSKU.product_id == product_id).all()


def get_sku(db: Session, sku_id: int):
    return db.query(models.ProductSKU).filter(models.ProductSKU.id == sku_id).first()


def create_sku(db: Session, product_id: int, sku: schemas.ProductSKUCreate):
    db_sku = models.ProductSKU(product_id=product_id, **sku.dict())
    db.add(db_sku)
    db.commit()
    db.refresh(db_sku)
    update_product_total_stock(db, product_id)
    return db_sku


def update_sku(db: Session, sku_id: int, sku: schemas.ProductSKUUpdate):
    db_sku = get_sku(db, sku_id)
    if not db_sku:
        return None
    update_data = sku.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sku, key, value)
    db.commit()
    db.refresh(db_sku)
    update_product_total_stock(db, db_sku.product_id)
    return db_sku


def delete_sku(db: Session, sku_id: int):
    db_sku = get_sku(db, sku_id)
    if not db_sku:
        return None
    product_id = db_sku.product_id
    db.delete(db_sku)
    db.commit()
    update_product_total_stock(db, product_id)
    return db_sku


def update_product_total_stock(db: Session, product_id: int):
    skus = get_skus_by_product(db, product_id)
    total_stock = sum([s.stock for s in skus]) if skus else 0
    product = get_product(db, product_id)
    if product:
        product.stock = total_stock
        db.commit()
        db.refresh(product)
    return product


def get_product_with_skus(db: Session, product_id: int):
    product = get_product(db, product_id)
    if not product:
        return None
    product.specs = get_specs_by_product(db, product_id)
    product.skus = get_skus_by_product(db, product_id)
    return product


def get_coupons(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.Coupon)
    if status:
        query = query.filter(models.Coupon.status == status)
    return query.offset(skip).limit(limit).all()


def get_coupon(db: Session, coupon_id: int):
    return db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()


def create_coupon(db: Session, coupon: schemas.CouponCreate):
    db_coupon = models.Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def update_coupon(db: Session, coupon_id: int, coupon: schemas.CouponUpdate):
    db_coupon = get_coupon(db, coupon_id)
    if not db_coupon:
        return None
    update_data = coupon.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_coupon, key, value)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def delete_coupon(db: Session, coupon_id: int):
    db_coupon = get_coupon(db, coupon_id)
    if not db_coupon:
        return None
    db.delete(db_coupon)
    db.commit()
    return db_coupon


def get_user_coupons(db: Session, user_id: int, status: str = None):
    query = db.query(models.UserCoupon).filter(models.UserCoupon.user_id == user_id)
    if status:
        query = query.filter(models.UserCoupon.status == status)
    return query.all()


def get_user_coupon(db: Session, user_coupon_id: int):
    return db.query(models.UserCoupon).filter(models.UserCoupon.id == user_coupon_id).first()


def claim_coupon(db: Session, user_id: int, coupon_id: int):
    from sqlalchemy.sql import func
    coupon = get_coupon(db, coupon_id)
    if not coupon:
        raise ValueError("优惠券不存在")
    if coupon.status != "active":
        raise ValueError("优惠券不可领取")
    if coupon.total_count > 0 and coupon.used_count >= coupon.total_count:
        raise ValueError("优惠券已领完")
    claimed = db.query(models.UserCoupon).filter(
        models.UserCoupon.user_id == user_id,
        models.UserCoupon.coupon_id == coupon_id
    ).count()
    if claimed >= coupon.per_limit:
        raise ValueError(f"每人限领 {coupon.per_limit} 张")
    db_user_coupon = models.UserCoupon(user_id=user_id, coupon_id=coupon_id, received_at=func.now())
    db.add(db_user_coupon)
    db.commit()
    db.refresh(db_user_coupon)
    return db_user_coupon


def use_coupon(db: Session, user_coupon_id: int, order_id: int):
    from sqlalchemy.sql import func
    user_coupon = get_user_coupon(db, user_coupon_id)
    if not user_coupon:
        raise ValueError("用户优惠券不存在")
    if user_coupon.status != "unused":
        raise ValueError("优惠券已使用或已过期")
    coupon = get_coupon(db, user_coupon.coupon_id)
    if coupon:
        coupon.used_count += 1
    user_coupon.status = "used"
    user_coupon.order_id = order_id
    user_coupon.used_at = func.now()
    db.commit()
    db.refresh(user_coupon)
    return user_coupon


def calculate_discount(db: Session, coupon_id: int, total_amount: float, product_ids: list = None, category: str = None):
    coupon = get_coupon(db, coupon_id)
    if not coupon:
        raise ValueError("优惠券不存在")
    if coupon.status != "active":
        raise ValueError("优惠券不可用")
    if total_amount < coupon.min_amount:
        raise ValueError(f"订单金额不满足最低消费 {coupon.min_amount} 元")
    if coupon.category and category and coupon.category != category:
        raise ValueError("优惠券不支持该商品分类")
    if coupon.product_ids and product_ids:
        allowed_ids = [int(i) for i in coupon.product_ids.split(",")]
        if not any(pid in allowed_ids for pid in product_ids):
            raise ValueError("优惠券不支持该商品")
    if coupon.type == "fixed":
        return min(coupon.value, total_amount)
    elif coupon.type == "percent":
        return total_amount * (coupon.value / 100)
    return 0


def get_after_sales(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.AfterSale)
    if status:
        query = query.filter(models.AfterSale.status == status)
    return query.offset(skip).limit(limit).all()


def get_after_sale(db: Session, after_sale_id: int):
    return db.query(models.AfterSale).filter(models.AfterSale.id == after_sale_id).first()


def get_after_sales_by_user(db: Session, user_id: int):
    return db.query(models.AfterSale).filter(models.AfterSale.user_id == user_id).all()


def get_after_sales_by_order(db: Session, order_id: int):
    return db.query(models.AfterSale).filter(models.AfterSale.order_id == order_id).all()


def create_after_sale(db: Session, user_id: int, after_sale: schemas.AfterSaleCreate):
    order = get_order(db, after_sale.order_id)
    if not order:
        raise ValueError("订单不存在")
    if order.user_id != user_id:
        raise ValueError("无权操作该订单")
    if order.status not in ["paid", "shipped", "completed"]:
        raise ValueError("订单状态不支持售后")
    db_after_sale = models.AfterSale(
        user_id=user_id,
        order_id=after_sale.order_id,
        order_item_id=after_sale.order_item_id,
        type=after_sale.type,
        reason=after_sale.reason,
        description=after_sale.description,
        images=after_sale.images,
        refund_amount=after_sale.refund_amount
    )
    db.add(db_after_sale)
    db.commit()
    db.refresh(db_after_sale)
    return db_after_sale


def update_after_sale(db: Session, after_sale_id: int, after_sale: schemas.AfterSaleUpdate, approved_by: int = None):
    from sqlalchemy.sql import func
    db_after_sale = get_after_sale(db, after_sale_id)
    if not db_after_sale:
        return None
    if after_sale.status:
        db_after_sale.status = after_sale.status
        if after_sale.status == "approved":
            db_after_sale.approved_at = func.now()
            db_after_sale.approved_by = approved_by
        elif after_sale.status == "rejected":
            db_after_sale.reject_reason = after_sale.reject_reason
    update_data = after_sale.dict(exclude_unset=True, exclude={"status", "reject_reason"})
    for key, value in update_data.items():
        setattr(db_after_sale, key, value)
    db.commit()
    db.refresh(db_after_sale)
    return db_after_sale
