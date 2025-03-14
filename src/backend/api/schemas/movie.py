from pydantic import Field, PositiveInt

from .base import Base
from ..utils import Lowercase

class _MovieBase(Base):
    title: str
    duration: PositiveInt
    year: PositiveInt = Field(ge=1700)

class MovieCreate(_MovieBase):
    genres: list[Lowercase] = []

class MovieRead(_MovieBase):
    id: PositiveInt
    genres: list[Lowercase] = []

class MovieUpdate(Base):
    title: str | None = None
    duration: PositiveInt | None = None
    year: PositiveInt | None = Field(None, ge=1700)
    genres: list[Lowercase] | None = None
