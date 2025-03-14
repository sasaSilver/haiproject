from pydantic import PositiveInt, EmailStr

from .base import Base

class _UserBase(Base):
    name: str
    email: EmailStr
    gender: str
    country: str

class UserRead(_UserBase):
    id: PositiveInt

class UserCreate(_UserBase):
    password: str

class User(UserCreate):
    id: PositiveInt

class UserUpdate(Base):
    name: str | None = None
    email: EmailStr | None = None
    gender: str | None = None
    country: str | None = None
    password: str | None = None
