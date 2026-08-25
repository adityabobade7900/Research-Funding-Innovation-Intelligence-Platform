from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from app.schemas.profile import ProfileRead, ProfileUpdate


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.RESEARCHER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    profile: Optional[ProfileUpdate] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    profile: Optional[ProfileRead] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None
