from pydantic import Field

from .base import Base
from .genre import GenreRead, GenreUpdate

class _MovieBase(Base):
    title: str
    duration: int = Field(example=1000, description="Duration in seconds")
    image: str
    year: int = Field(example=2000)

class MovieCreate(_MovieBase):
    genres: list[str]

class MovieRead(_MovieBase):
    id: int
    genres: list[GenreRead]

class MovieUpdate(Base):
    title: str | None = None
    duration: int | None = None
    year: int | None = None
    genres: list[GenreUpdate] | None = None
