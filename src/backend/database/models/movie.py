from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import Base
from .rating import RatingSchema
from .genre import movie_genre, GenreSchema

class MovieSchema(Base):
    __tablename__ = "movies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column()
    year: Mapped[int] = mapped_column()
    
    ratings: Mapped[set[RatingSchema] | None] = relationship(
        back_populates="movie",
        cascade="all, delete"
    )
    
    genres: Mapped[set[GenreSchema] | None] = relationship(
        secondary=movie_genre,
        back_populates="movies",
        cascade="all, delete",
        lazy="select"
    )
