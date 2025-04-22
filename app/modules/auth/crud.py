from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from app.modules.auth import models, schemas
from app.core.config import settings
from app.modules.auth.oauth2 import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_social_id(db: Session, provider: str, social_id: str):
    return db.query(models.User).filter(
        models.User.provider == provider,
        models.User.social_id == social_id
    ).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_social_user(
    db: Session,
    provider: str,
    social_id: str,
    email: Optional[str],
    name: Optional[str],
    avatar: Optional[str]
):
    db_user = models.User(
        email=email or f"{provider}_{social_id}@social.local",
        hashed_password=None,
        provider=provider,
        social_id=social_id,
        name=name,
        avatar=avatar
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_refresh_token(db: Session, refresh_token: schemas.RefreshTokenCreate):
    db_refresh_token = models.RefreshToken(
        user_id=refresh_token.user_id,
        token=refresh_token.token,
        expires_at=refresh_token.expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)
    return db_refresh_token

def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token
    ).first()

def revoke_refresh_token(db: Session, token: str):
    db_token = get_refresh_token(db, token)
    if db_token:
        db_token.is_active = False
        db.commit()
        db.refresh(db_token)
    return db_token