from .base import Base
from .movie import MovieRead

class UserRead(Base):
    name: str
    id: int

class UserRating(Base):
    movie: MovieRead
    rating: float

class CurrentUser(Base):
    id: int
    name:str
    ratings: list[UserRating] = []
    recommendations: list[MovieRead] = []

class UserCreate(Base):
    name: str
    password: str

class UserUpdate(Base):
    name: str | None = None
