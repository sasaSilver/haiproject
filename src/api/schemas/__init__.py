from .movie import MovieCreate, MovieRead, MovieUpdate
from .genre import GenreCreate, GenreRead, GenreUpdate
from .user import UserCreate, UserRead, UserUpdate, UserLogin
from .rating import Rating, RatingUpdate
from .token import Token, TokenData

Rating.model_rebuild()
