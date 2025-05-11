from pydantic import Field

from .base import Base
from .genre import GenreRead, GenreUpdate

class _MovieBase(Base):
    popularity: float
    title: str
    vote_average: float
    vote_count: int
    description: str
    year: int

class MovieCreate(_MovieBase):
    genres: list[str]

class MovieRead(_MovieBase):
    id: str
    genres: list[GenreRead]

class MovieUpdate(Base):
    title: str | None = None
    duration: int | None = None
    image: str | None = None
    rating: float | None = None
    description: str | None = None
    year: int | None = None
    genres: list[GenreUpdate] | None = None
