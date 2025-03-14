from .movie import MovieSchema, GenreSchema, movie_genre
from .user import UserSchema
from .rating import RatingSchema

__all__ = [
    "RatingSchema",
    "GenreSchema",
    "MovieSchema",
    "UserSchema",
    "movie_genre"
]
