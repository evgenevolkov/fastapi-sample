from datetime import datetime
from decouple import config
from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional


### User
class UserRole(str, Enum):
    ROLE_ADMIN = config("ROLE_ADMIN")
    ROLE_END_USER = config("ROLE_END_USER")
    

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.ROLE_END_USER


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class ConfigDict:
        from_attributes = True
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCurrent(BaseModel):
    id: int
    role: UserRole


### Token
class Token(BaseModel):
    access_token: str
    token_type: str
    expire_at: datetime


class TokenData(BaseModel):
    user_id: Optional[int]


### Text
class TextCreate(BaseModel):
    name: str
    content: str


class TextOut(BaseModel):
    id: int
    user_id: int
    name: str
    content: str
    created_at: datetime
    owner: UserOut