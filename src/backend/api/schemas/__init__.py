from .movie import MovieCreate, MovieRead, MovieUpdate
from .genre import GenreCreate, GenreRead, GenreUpdate
from .user import UserCreate, UserRead, UserUpdate
from .rating import Rating, RatingUpdate

__all__ = [
    "Rating",
    "RatingUpdate",
    "MovieCreate",
    "MovieRead",
    "MovieUpdate",
    "GenreCreate",
    "GenreRead",
    "GenreUpdate",
    "UserCreate",
    "UserRead",
    "UserUpdate"
]

Rating.model_rebuild()
