from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    user_id: int | None = None
    email: Optional[str] = None

class RefreshTokenCreate(BaseModel):
    user_id: int
    token: str
    expires_at: datetime

class RefreshTokenInDB(RefreshTokenCreate):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserSocialCreate(BaseModel):
    provider: str
    social_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    provider: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True