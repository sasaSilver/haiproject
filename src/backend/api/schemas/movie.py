from typing import Annotated

from pydantic import Field, PositiveInt, StringConstraints

from .base import Base

Lowercase = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]+$", to_lower=True)]

class _MovieBase(Base):
    title: str
    duration: PositiveInt
    year: PositiveInt = Field(ge=1700)

class MovieCreate(_MovieBase):
    genres: list[Lowercase] = []

class Movie(_MovieBase):
    id: PositiveInt
    genres: list[Lowercase] = []

class MovieUpdate(Base):
    title: str | None = None
    duration: PositiveInt | None = None
    year: PositiveInt | None = Field(None, ge=1700)
    genres: list[Lowercase] | None = None
