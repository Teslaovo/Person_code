from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from . import crud, schemas, models
from .database import get_db
from .auth import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    get_admin_user
)

router = APIRouter()


def success_response(data=None):
    return {"code": 200, "message": "ok", "data": data}


def error_response(code: int, message: str):
    return {"code": code, "message": message, "data": None}


# 用户注册接口 - 不需要认证
@router.post("/api/register")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # 注册用户默认角色为普通用户
    user.role = "user"
    created_user = crud.create_user(db=db, user=user)
    # 注册成功后自动登录
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": created_user.username}, expires_delta=access_token_expires
    )
    user_response = schemas.UserResponse.from_orm(created_user)
    return success_response({
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    })


# 登录接口 - 不需要认证
@router.post("/api/login")
async def login(form_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_response = schemas.UserResponse.from_orm(user)
    return success_response({
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    })


# 验证用户是否存在 - 公开接口（供购物服务调用）
@router.get("/api/users/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    return success_response({
        "exists": user is not None,
        "user_id": user_id
    })


# 获取当前登录用户信息 - 需要登录
@router.get("/api/users/me")
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return success_response(schemas.UserResponse.from_orm(current_user))


# 用户列表 - 仅管理员
@router.get("/api/users")
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return success_response([schemas.UserResponse.from_orm(u) for u in users])


# 用户详情 - 仅管理员
@router.get("/api/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user)
):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(schemas.UserResponse.from_orm(user))


# 创建用户 - 仅管理员
@router.post("/api/users")
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user)
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    created_user = crud.create_user(db=db, user=user)
    return success_response(schemas.UserResponse.from_orm(created_user))


# 更新用户 - 仅管理员
@router.put("/api/users/{user_id}")
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user)
):
    updated_user = crud.update_user(db, user_id=user_id, user=user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(schemas.UserResponse.from_orm(updated_user))


# 删除用户 - 仅管理员
@router.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user)
):
    deleted_user = crud.delete_user(db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(schemas.UserResponse.from_orm(deleted_user))


# 地址管理 API
# 获取用户地址列表 - 需要登录
@router.get("/api/addresses")
def get_addresses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    addresses = crud.get_addresses_by_user(db, user_id=current_user.id)
    return success_response([schemas.AddressResponse.from_orm(a) for a in addresses])


# 获取地址详情 - 需要登录
@router.get("/api/addresses/{address_id}")
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    address = crud.get_address(db, address_id=address_id)
    if address is None or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")
    return success_response(schemas.AddressResponse.from_orm(address))


# 创建地址 - 需要登录
@router.post("/api/addresses")
def create_address(
    address: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    created = crud.create_address(db, user_id=current_user.id, address=address)
    return success_response(schemas.AddressResponse.from_orm(created))


# 更新地址 - 需要登录
@router.put("/api/addresses/{address_id}")
def update_address(
    address_id: int,
    address: schemas.AddressUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_address = crud.get_address(db, address_id=address_id)
    if db_address is None or db_address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")
    updated = crud.update_address(db, address_id=address_id, address=address)
    return success_response(schemas.AddressResponse.from_orm(updated))


# 删除地址 - 需要登录
@router.delete("/api/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_address = crud.get_address(db, address_id=address_id)
    if db_address is None or db_address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")
    deleted = crud.delete_address(db, address_id=address_id)
    return success_response(schemas.AddressResponse.from_orm(deleted))
