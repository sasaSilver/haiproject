from pydantic import Field, PositiveInt

from .base import Base

class Rating(Base):
    user_id: PositiveInt
    movie_id: PositiveInt
    rating: PositiveInt = Field(ge=0, le=10)

class RatingUpdate(Base):
    user_id: PositiveInt | None = None
    movie_id: PositiveInt | None = None
    rating: PositiveInt | None = Field(None, ge=0, le=10)
