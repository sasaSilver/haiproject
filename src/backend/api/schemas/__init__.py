from .movie import Movie, MovieCreate, MovieUpdate
from .user import User, UserCreate, UserRead, UserUpdate
from .rating import Rating, RatingUpdate

__all__ = [
    "Rating",
    "RatingUpdate",
    "Movie",
    "MovieCreate",
    "MovieUpdate",
    "User",
    "UserRead",
    "UserCreate",
    "UserUpdate"
]

Rating.model_rebuild()
