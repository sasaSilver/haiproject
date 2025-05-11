from .base import Base

class Rating(Base):
    user_id: int
    movie_id: int
    rating: float

class RatingUpdate(Base):
    user_id: int | None = None
    movie_id: int | None = None
    rating: float | None = None
