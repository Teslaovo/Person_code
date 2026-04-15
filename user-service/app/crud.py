from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed_password,
        nickname=user.nickname,
        phone=user.phone,
        role=user.role or "user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user


# 地址相关操作
def get_address(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()


def get_addresses_by_user(db: Session, user_id: int):
    return db.query(models.Address).filter(models.Address.user_id == user_id).all()


def create_address(db: Session, user_id: int, address: schemas.AddressCreate):
    # 如果是默认地址，先取消其他地址的默认状态
    if address.is_default == 1:
        db.query(models.Address).filter(models.Address.user_id == user_id).update({"is_default": 0})
    db_address = models.Address(user_id=user_id, **address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def update_address(db: Session, address_id: int, address: schemas.AddressUpdate):
    db_address = get_address(db, address_id)
    if not db_address:
        return None
    update_data = address.dict(exclude_unset=True)
    # 如果设置为默认地址，先取消其他地址的默认状态
    if update_data.get("is_default") == 1:
        db.query(models.Address).filter(models.Address.user_id == db_address.user_id).update({"is_default": 0})
    for key, value in update_data.items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    return db_address


def delete_address(db: Session, address_id: int):
    db_address = get_address(db, address_id)
    if not db_address:
        return None
    db.delete(db_address)
    db.commit()
    return db_address
