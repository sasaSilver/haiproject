from .base import Base

class GenreCreate(Base):
    name: str

class GenreRead(GenreCreate):
    id: int

class GenreUpdate(Base):
    id: int | None = None
    name: str | None = None
