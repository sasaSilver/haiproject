from sqlalchemy import CheckConstraint
from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import Base
from .rating import RatingSchema
from .genre import movie_genre, GenreSchema

class MovieSchema(Base):
    __tablename__ = "movies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    image: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column(
        CheckConstraint("duration > 0", name="positive_duration"),
    )
    year: Mapped[int] = mapped_column(
        CheckConstraint("year > 1700", name="year_gt_1700")
    )
    ratings: Mapped[set[RatingSchema] | None] = relationship(
        back_populates="movie",
        cascade="all, delete",
        lazy="selectin"
    )
    
    genres: Mapped[set[GenreSchema] | None] = relationship(
        secondary=movie_genre,
        back_populates="movies",
        cascade="all, delete",
        lazy="selectin"
    )
