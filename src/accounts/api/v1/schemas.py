from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    id: int
    username: Optional[str] = None
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithTokensResponse(BaseModel):
    access: str
    refresh: str
    user: UserResponse


class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str
