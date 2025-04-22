from .base import Base

class _UserBase(Base):
    name: str

class UserRead(_UserBase):
    id: int

class UserCreate(_UserBase):
    password: str

class UserUpdate(Base):
    name: str | None = None
    
class UserLogin(Base):
    username : str
    password : str
