from .base import Base

class _UserBase(Base):
    name: str
    email: str
    gender: str
    country: str

class UserRead(_UserBase):
    id: int

class UserCreate(_UserBase):
    password: str

class UserUpdate(Base):
    name: str | None = None
    email: str | None = None
    gender: str | None = None
    country: str | None = None
    password: str | None = None
