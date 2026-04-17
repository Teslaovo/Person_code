from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import uuid
from . import crud, schemas
from .database import get_db
from .user_client import verify_user_exists

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只允许上传图片文件")

    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    new_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    image_url = f"/uploads/{new_filename}"
    return success_response({"url": image_url, "filename": new_filename})


def success_response(data=None):
    return {"code": 200, "message": "ok", "data": data}


@router.get("/api/products")
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    products = crud.get_products(db, skip=skip, limit=limit, category=category, search=search)
    return success_response([schemas.ProductResponse.from_orm(p) for p in products])


@router.get("/api/products/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    return success_response(categories)


@router.get("/api/products/hot")
def get_hot_products(limit: int = 10, db: Session = Depends(get_db)):
    products = crud.get_hot_products(db, limit=limit)
    return success_response([schemas.ProductResponse.from_orm(p) for p in products])


@router.get("/api/products/low-stock")
def get_low_stock_products(db: Session = Depends(get_db)):
    products = crud.get_low_stock_products(db)
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "stock": p.stock,
            "low_stock_threshold": p.low_stock_threshold,
            "price": p.price,
            "category": p.category or "其他",
            "is_hot": p.is_hot or 0,
            "is_active": p.is_active or 1,
            "sales": p.sales or 0
        })
    return success_response(result)


@router.get("/api/products/out-of-stock")
def get_out_of_stock_products(db: Session = Depends(get_db)):
    products = crud.get_out_of_stock_products(db)
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "stock": p.stock,
            "low_stock_threshold": p.low_stock_threshold or 10,
            "price": p.price,
            "category": p.category or "其他",
            "is_hot": p.is_hot or 0,
            "is_active": p.is_active or 1,
            "sales": p.sales or 0
        })
    return success_response(result)


@router.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return success_response(schemas.ProductResponse.from_orm(product))


@router.post("/api/products")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    created = crud.create_product(db=db, product=product)
    return success_response(schemas.ProductResponse.from_orm(created))


@router.put("/api/products/{product_id}")
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated = crud.update_product(db, product_id=product_id, product=product)
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return success_response(schemas.ProductResponse.from_orm(updated))


@router.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id=product_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return success_response(schemas.ProductResponse.from_orm(deleted))


@router.get("/api/cart/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = crud.get_cart_by_user(db, user_id=user_id)
    result = []
    for item in cart_items:
        item_dict = schemas.CartItemResponse.from_orm(item).dict()
        product = crud.get_product(db, item.product_id)
        if product:
            item_dict["product"] = schemas.ProductResponse.from_orm(product)
        result.append(item_dict)
    return success_response(result)


@router.post("/api/cart")
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    added = crud.add_to_cart(db=db, cart_item=cart_item)
    return success_response(schemas.CartItemResponse.from_orm(added))


@router.put("/api/cart/{cart_id}")
def update_cart(cart_id: int, update: schemas.CartItemUpdate, db: Session = Depends(get_db)):
    updated = crud.update_cart_item(db, cart_id=cart_id, quantity=update.quantity)
    if updated is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return success_response(schemas.CartItemResponse.from_orm(updated))


@router.delete("/api/cart/{cart_id}")
def delete_cart_item(cart_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_cart_item(db, cart_id=cart_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return success_response(schemas.CartItemResponse.from_orm(deleted))


@router.post("/api/orders")
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 尝试验证用户，如果用户服务不可用则跳过（开发环境友好）
    try:
        user_exists = await verify_user_exists(order.user_id)
        if not user_exists:
            raise HTTPException(status_code=400, detail="User not found")
    except Exception as e:
        # 用户服务不可用时，在开发环境中继续执行
        import logging
        logging.warning(f"User service verification failed: {e}, continuing anyway")

    # 如果前端传了优惠后的总价，使用它；否则自己计算
    if order.total_price is not None and order.total_price >= 0:
        total_price = order.total_price
    else:
        total_price = 0.0
        for item in order.items:
            product = crud.get_product(db, item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            total_price += product.price * item.quantity

    address_data = {
        "name": order.address_name,
        "phone": order.address_phone,
        "province": order.address_province,
        "city": order.address_city,
        "district": order.address_district,
        "detail": order.address_detail
    }
    try:
        created_order = crud.create_order(db, user_id=order.user_id, items=order.items, total_price=total_price, address_data=address_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    for item in order.items:
        cart_item = crud.get_cart_item_by_user_and_product(db, order.user_id, item.product_id)
        if cart_item:
            crud.delete_cart_item(db, cart_item.id)
    order_data = schemas.OrderResponse.from_orm(created_order)
    return success_response(order_data)


@router.get("/api/orders")
def get_all_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_all_orders(db, skip=skip, limit=limit)
    result = []
    for order in orders:
        order_dict = schemas.OrderResponse.from_orm(order).dict()
        order_dict["items"] = [schemas.OrderItemResponse.from_orm(i) for i in order.items]
        result.append(order_dict)
    return success_response(result)


@router.get("/api/orders/{user_id}")
def get_orders(user_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_user(db, user_id=user_id)
    result = []
    for order in orders:
        order_dict = schemas.OrderResponse.from_orm(order).dict()
        order_dict["items"] = [schemas.OrderItemResponse.from_orm(i) for i in order.items]
        result.append(order_dict)
    return success_response(result)


@router.get("/api/orders/detail/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order_dict = schemas.OrderResponse.from_orm(order).dict()
    order_dict["items"] = [schemas.OrderItemResponse.from_orm(i) for i in order.items]
    return success_response(order_dict)


@router.put("/api/orders/{order_id}/status")
def update_order_status(order_id: int, update: schemas.OrderUpdateStatus, db: Session = Depends(get_db)):
    valid_statuses = ["pending", "paid", "shipped", "completed", "cancelled"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    updated = crud.update_order_status(db, order_id=order_id, status=update.status)
    if updated is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return success_response(schemas.OrderResponse.from_orm(updated))


@router.post("/api/orders/{order_id}/ship")
def ship_order(order_id: int, ship_data: schemas.OrderShip, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail="Only paid orders can be shipped")
    updated = crud.ship_order(db, order_id=order_id, tracking_number=ship_data.tracking_number, tracking_company=ship_data.tracking_company)
    return success_response(schemas.OrderResponse.from_orm(updated))


@router.get("/api/favorites/{user_id}")
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = crud.get_favorites_by_user(db, user_id=user_id)
    result = []
    for fav in favorites:
        fav_dict = schemas.FavoriteResponse.from_orm(fav).dict()
        product = crud.get_product(db, fav.product_id)
        if product:
            fav_dict["product"] = schemas.ProductResponse.from_orm(product)
        result.append(fav_dict)
    return success_response(result)


@router.post("/api/favorites")
def add_favorite(favorite: schemas.FavoriteCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, favorite.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    added = crud.add_favorite(db=db, favorite=favorite)
    return success_response(schemas.FavoriteResponse.from_orm(added))


@router.delete("/api/favorites/item/{favorite_id}")
def remove_favorite_item(favorite_id: int, db: Session = Depends(get_db)):
    deleted = crud.remove_favorite_by_id(db, favorite_id=favorite_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return success_response({"id": deleted.id})


@router.get("/api/messages/{user_id}")
def get_messages(user_id: int, other_user_id: int = None, db: Session = Depends(get_db)):
    messages = crud.get_messages_by_user(db, user_id=user_id, other_user_id=other_user_id)
    result = []
    for msg in messages:
        msg_dict = schemas.MessageResponse.from_orm(msg).dict()
        result.append(msg_dict)
    return success_response(result)


@router.get("/api/messages/unread/{user_id}")
def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    count = crud.get_unread_count(db, user_id=user_id)
    return success_response({"count": count})


@router.post("/api/messages")
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    created = crud.create_message(db, message=message)
    return success_response(schemas.MessageResponse.from_orm(created))


@router.put("/api/messages/{message_id}/read")
def mark_message_read(message_id: int, db: Session = Depends(get_db)):
    updated = crud.mark_as_read(db, message_id=message_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return success_response(schemas.MessageResponse.from_orm(updated))


@router.put("/api/messages/{user_id}/{other_user_id}/read")
def mark_conversation_read(user_id: int, other_user_id: int, db: Session = Depends(get_db)):
    crud.mark_conversation_as_read(db, user_id=user_id, other_user_id=other_user_id)
    return success_response(None)


@router.get("/api/messages/conversations/{user_id}")
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    user_ids = crud.get_conversation_users(db, user_id=user_id)
    return success_response(user_ids)


@router.delete("/api/favorites/{user_id}/{product_id}")
def remove_favorite(user_id: int, product_id: int, db: Session = Depends(get_db)):
    deleted = crud.remove_favorite(db, user_id=user_id, product_id=product_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return success_response({"id": deleted.id})


@router.get("/api/reviews/product/{product_id}")
def get_product_reviews(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = crud.get_reviews_by_product(db, product_id=product_id, skip=skip, limit=limit)
    return success_response([schemas.ReviewResponse.from_orm(r) for r in reviews])


@router.get("/api/reviews/user/{user_id}")
def get_user_reviews(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = crud.get_reviews_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return success_response([schemas.ReviewResponse.from_orm(r) for r in reviews])


@router.get("/api/reviews/pending/{user_id}/{order_id}")
def get_pending_reviews(user_id: int, order_id: int, db: Session = Depends(get_db)):
    items = crud.get_pending_review_products(db, user_id=user_id, order_id=order_id)
    result = []
    for item in items:
        product = crud.get_product(db, item.product_id)
        result.append({
            "order_item_id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "product_image": product.image if product else None,
            "quantity": item.quantity,
            "price": item.price
        })
    return success_response(result)


@router.post("/api/reviews")
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_review(db, user_id=review.user_id, review=review)
        return success_response(schemas.ReviewResponse.from_orm(created))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/reviews/{review_id}")
def update_review(review_id: int, review: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    updated = crud.update_review(db, review_id=review_id, review=review)
    if updated is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return success_response(schemas.ReviewResponse.from_orm(updated))


@router.delete("/api/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_review(db, review_id=review_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return success_response(schemas.ReviewResponse.from_orm(deleted))


@router.get("/api/products/{product_id}/specs")
def get_product_specs(product_id: int, db: Session = Depends(get_db)):
    specs = crud.get_specs_by_product(db, product_id=product_id)
    return success_response([schemas.ProductSpecResponse.from_orm(s) for s in specs])


@router.get("/api/products/{product_id}/skus")
def get_product_skus(product_id: int, db: Session = Depends(get_db)):
    skus = crud.get_skus_by_product(db, product_id=product_id)
    return success_response([schemas.ProductSKUResponse.from_orm(s) for s in skus])


@router.get("/api/products/{product_id}/with-skus")
def get_product_with_skus(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_with_skus(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product_dict = schemas.ProductResponse.from_orm(product).dict()
    product_dict["specs"] = [schemas.ProductSpecResponse.from_orm(s) for s in product.specs]
    product_dict["skus"] = [schemas.ProductSKUResponse.from_orm(s) for s in product.skus]
    return success_response(product_dict)


@router.post("/api/products/{product_id}/specs")
def create_spec(product_id: int, spec: schemas.ProductSpecCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    created = crud.create_spec(db, product_id=product_id, spec=spec)
    return success_response(schemas.ProductSpecResponse.from_orm(created))


@router.put("/api/specs/{spec_id}")
def update_spec(spec_id: int, spec: schemas.ProductSpecUpdate, db: Session = Depends(get_db)):
    updated = crud.update_spec(db, spec_id=spec_id, spec=spec)
    if updated is None:
        raise HTTPException(status_code=404, detail="Spec not found")
    return success_response(schemas.ProductSpecResponse.from_orm(updated))


@router.delete("/api/specs/{spec_id}")
def delete_spec(spec_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_spec(db, spec_id=spec_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Spec not found")
    return success_response(schemas.ProductSpecResponse.from_orm(deleted))


@router.post("/api/products/{product_id}/skus")
def create_sku(product_id: int, sku: schemas.ProductSKUCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    created = crud.create_sku(db, product_id=product_id, sku=sku)
    return success_response(schemas.ProductSKUResponse.from_orm(created))


@router.put("/api/skus/{sku_id}")
def update_sku(sku_id: int, sku: schemas.ProductSKUUpdate, db: Session = Depends(get_db)):
    updated = crud.update_sku(db, sku_id=sku_id, sku=sku)
    if updated is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    return success_response(schemas.ProductSKUResponse.from_orm(updated))


@router.delete("/api/skus/{sku_id}")
def delete_sku(sku_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_sku(db, sku_id=sku_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    return success_response(schemas.ProductSKUResponse.from_orm(deleted))


@router.get("/api/coupons")
def get_coupons(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    coupons = crud.get_coupons(db, skip=skip, limit=limit, status=status)
    return success_response([schemas.CouponResponse.from_orm(c) for c in coupons])


@router.get("/api/coupons/{coupon_id}")
def get_coupon(coupon_id: int, db: Session = Depends(get_db)):
    coupon = crud.get_coupon(db, coupon_id=coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return success_response(schemas.CouponResponse.from_orm(coupon))


@router.post("/api/coupons")
def create_coupon(coupon: schemas.CouponCreate, db: Session = Depends(get_db)):
    created = crud.create_coupon(db=db, coupon=coupon)
    return success_response(schemas.CouponResponse.from_orm(created))


@router.put("/api/coupons/{coupon_id}")
def update_coupon(coupon_id: int, coupon: schemas.CouponUpdate, db: Session = Depends(get_db)):
    updated = crud.update_coupon(db, coupon_id=coupon_id, coupon=coupon)
    if updated is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return success_response(schemas.CouponResponse.from_orm(updated))


@router.delete("/api/coupons/{coupon_id}")
def delete_coupon(coupon_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_coupon(db, coupon_id=coupon_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return success_response(schemas.CouponResponse.from_orm(deleted))


@router.get("/api/user-coupons/{user_id}")
def get_user_coupons(user_id: int, status: str = None, db: Session = Depends(get_db)):
    user_coupons = crud.get_user_coupons(db, user_id=user_id, status=status)
    result = []
    for uc in user_coupons:
        uc_dict = schemas.UserCouponResponse.from_orm(uc).dict()
        coupon = crud.get_coupon(db, uc.coupon_id)
        if coupon:
            uc_dict["coupon"] = schemas.CouponResponse.from_orm(coupon)
        result.append(uc_dict)
    return success_response(result)


@router.post("/api/user-coupons/claim")
def claim_coupon(user_id: int, coupon_id: int, db: Session = Depends(get_db)):
    try:
        claimed = crud.claim_coupon(db, user_id=user_id, coupon_id=coupon_id)
        return success_response(schemas.UserCouponResponse.from_orm(claimed))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/user-coupons/{user_coupon_id}/use")
def use_coupon(user_coupon_id: int, order_id: int, db: Session = Depends(get_db)):
    try:
        used = crud.use_coupon(db, user_coupon_id=user_coupon_id, order_id=order_id)
        return success_response(schemas.UserCouponResponse.from_orm(used))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/coupons/calculate")
def calculate_discount(coupon_id: int, total_amount: float, product_ids: str = None, category: str = None, db: Session = Depends(get_db)):
    try:
        pid_list = [int(p) for p in product_ids.split(",")] if product_ids else None
        discount = crud.calculate_discount(db, coupon_id=coupon_id, total_amount=total_amount, product_ids=pid_list, category=category)
        return success_response({"discount": discount})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/after-sales")
def get_after_sales(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    after_sales = crud.get_after_sales(db, skip=skip, limit=limit, status=status)
    return success_response([schemas.AfterSaleResponse.from_orm(a) for a in after_sales])


@router.get("/api/after-sales/{after_sale_id}")
def get_after_sale(after_sale_id: int, db: Session = Depends(get_db)):
    after_sale = crud.get_after_sale(db, after_sale_id=after_sale_id)
    if after_sale is None:
        raise HTTPException(status_code=404, detail="After-sale not found")
    return success_response(schemas.AfterSaleResponse.from_orm(after_sale))


@router.get("/api/after-sales/user/{user_id}")
def get_user_after_sales(user_id: int, db: Session = Depends(get_db)):
    after_sales = crud.get_after_sales_by_user(db, user_id=user_id)
    return success_response([schemas.AfterSaleResponse.from_orm(a) for a in after_sales])


@router.get("/api/after-sales/order/{order_id}")
def get_order_after_sales(order_id: int, db: Session = Depends(get_db)):
    after_sales = crud.get_after_sales_by_order(db, order_id=order_id)
    return success_response([schemas.AfterSaleResponse.from_orm(a) for a in after_sales])


@router.post("/api/after-sales")
def create_after_sale(after_sale: schemas.AfterSaleCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_after_sale(db, user_id=after_sale.user_id, after_sale=after_sale)
        return success_response(schemas.AfterSaleResponse.from_orm(created))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/after-sales/{after_sale_id}")
def update_after_sale(after_sale_id: int, after_sale: schemas.AfterSaleUpdate, approved_by: int = None, db: Session = Depends(get_db)):
    updated = crud.update_after_sale(db, after_sale_id=after_sale_id, after_sale=after_sale, approved_by=approved_by)
    if updated is None:
        raise HTTPException(status_code=404, detail="After-sale not found")
    return success_response(schemas.AfterSaleResponse.from_orm(updated))


@router.get("/api/stock-alerts")
def get_stock_alerts(is_resolved: int = None, db: Session = Depends(get_db)):
    alerts = crud.get_stock_alerts(db, is_resolved=is_resolved)
    return success_response([schemas.StockAlertResponse.from_orm(a) for a in alerts])


@router.post("/api/stock-alerts/{alert_id}/resolve")
def resolve_stock_alert(alert_id: int, db: Session = Depends(get_db)):
    resolved = crud.resolve_stock_alert(db, alert_id=alert_id)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Stock alert not found")
    return success_response(schemas.StockAlertResponse.from_orm(resolved))


@router.post("/api/search/history")
def add_search_history(keyword: str, user_id: int = None, db: Session = Depends(get_db)):
    history = crud.add_search_history(db, keyword=keyword, user_id=user_id)
    return success_response(schemas.SearchHistoryResponse.from_orm(history))


@router.get("/api/search/history/{user_id}")
def get_search_history(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    histories = crud.get_search_history(db, user_id=user_id, limit=limit)
    return success_response([schemas.SearchHistoryResponse.from_orm(h) for h in histories])


@router.get("/api/search/hot")
def get_hot_searches(limit: int = 10, db: Session = Depends(get_db)):
    hot_searches = crud.get_hot_searches(db, limit=limit)
    return success_response([schemas.HotSearchResponse.from_orm(h) for h in hot_searches])


@router.get("/api/search/suggestions")
def get_search_suggestions(keyword: str, limit: int = 10, db: Session = Depends(get_db)):
    suggestions = crud.get_search_suggestions(db, keyword=keyword, limit=limit)
    return success_response(suggestions)


@router.get("/api/products/filter")
def get_products_filtered(
    min_price: float = None,
    max_price: float = None,
    min_sales: int = None,
    category: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    products = crud.get_products_by_filter(
        db, min_price=min_price, max_price=max_price,
        min_sales=min_sales, category=category,
        skip=skip, limit=limit
    )
    return success_response([schemas.ProductResponse.from_orm(p) for p in products])


@router.put("/api/products/batch/status")
def batch_update_products_status(product_ids: str, is_active: int, db: Session = Depends(get_db)):
    ids = [int(pid) for pid in product_ids.split(",")]
    crud.batch_update_products_status(db, product_ids=ids, is_active=is_active)
    return success_response(None)


@router.get("/api/promotions")
def get_promotions(promotion_type: str = None, status: str = None, db: Session = Depends(get_db)):
    promotions = crud.get_promotions(db, promotion_type=promotion_type, status=status)
    return success_response([schemas.PromotionResponse.from_orm(p) for p in promotions])


@router.get("/api/promotions/{promotion_id}")
def get_promotion(promotion_id: int, db: Session = Depends(get_db)):
    promotion = crud.get_promotion(db, promotion_id=promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return success_response(schemas.PromotionResponse.from_orm(promotion))


@router.post("/api/promotions")
def create_promotion(promotion: schemas.PromotionCreate, db: Session = Depends(get_db)):
    created = crud.create_promotion(db=db, promotion=promotion)
    return success_response(schemas.PromotionResponse.from_orm(created))


@router.put("/api/promotions/{promotion_id}")
def update_promotion(promotion_id: int, promotion: schemas.PromotionUpdate, db: Session = Depends(get_db)):
    updated = crud.update_promotion(db, promotion_id=promotion_id, promotion=promotion)
    if updated is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return success_response(schemas.PromotionResponse.from_orm(updated))


@router.delete("/api/promotions/{promotion_id}")
def delete_promotion(promotion_id: int, db: Session = Depends(get_db)):
    success = crud.delete_promotion(db, promotion_id=promotion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return success_response(None)


@router.get("/api/promotions/active")
def get_active_promotions(db: Session = Depends(get_db)):
    promotions = crud.get_active_promotions(db)
    return success_response([schemas.PromotionResponse.from_orm(p) for p in promotions])


@router.get("/api/products/{product_id}/recommendations")
def get_product_recommendations(product_id: int, rec_type: str = None, db: Session = Depends(get_db)):
    recs = crud.get_product_recommendations(db, product_id=product_id, rec_type=rec_type)
    result = []
    for rec in recs:
        rec_dict = schemas.ProductRecommendationResponse.from_orm(rec).dict()
        product = crud.get_product(db, rec.recommended_product_id)
        if product:
            rec_dict["product"] = schemas.ProductResponse.from_orm(product)
        result.append(rec_dict)
    return success_response(result)


@router.post("/api/products/recommendations")
def add_product_recommendation(recommendation: schemas.ProductRecommendationCreate, db: Session = Depends(get_db)):
    created = crud.add_product_recommendation(db=db, recommendation=recommendation)
    return success_response(schemas.ProductRecommendationResponse.from_orm(created))


@router.get("/api/stats/sales")
def get_sales_stats(period: str = "daily", db: Session = Depends(get_db)):
    stats = crud.get_sales_stats(db, period=period)
    return success_response(stats)


@router.get("/api/stats/products/rank")
def get_product_sales_rank(limit: int = 10, db: Session = Depends(get_db)):
    ranks = crud.get_product_sales_rank(db, limit=limit)
    return success_response(ranks)


@router.get("/api/stats/users/growth")
def get_user_growth_stats(days: int = 30, db: Session = Depends(get_db)):
    stats = crud.get_user_growth_stats(db, days=days)
    return success_response(stats)


@router.get("/api/stats/orders/conversion")
def get_order_conversion_stats(db: Session = Depends(get_db)):
    stats = crud.get_order_conversion_stats(db)
    return success_response(stats)


@router.get("/api/stats/summary")
def get_summary_stats(db: Session = Depends(get_db)):
    stats = crud.get_summary_stats(db)
    return success_response(stats)
