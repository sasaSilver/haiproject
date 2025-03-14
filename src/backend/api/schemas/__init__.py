from .movie import MovieCreate, MovieRead, MovieUpdate
from .user import UserCreate, UserRead, UserUpdate
from .rating import Rating, RatingUpdate

__all__ = [
    "Rating",
    "RatingUpdate",
    "MovieCreate",
    "MovieRead",
    "MovieUpdate",
    "UserCreate",
    "UserRead",
    "UserUpdate"
]

Rating.model_rebuild()
