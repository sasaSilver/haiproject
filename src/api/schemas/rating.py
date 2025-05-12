from .base import Base

class Rating(Base):
    user_id: int
    movie_id: str
    rating: float
