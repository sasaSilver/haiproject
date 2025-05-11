from sqlalchemy.orm import mapped_column, relationship, Mapped
from .base import Base
from .rating import RatingSchema
from .genre import movie_genre, GenreSchema
from .keyword import movie_keyword, KeywordSchema

class MovieSchema(Base):
    __tablename__ = "movies"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    popularity: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column(index=True)
    vote_average: Mapped[float] = mapped_column()
    vote_count: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column()
    year: Mapped[int] = mapped_column()
    ratings: Mapped[set[RatingSchema]] = relationship(
        back_populates="movie",
        cascade="all, delete"
    )
    
    genres: Mapped[set[GenreSchema]] = relationship(
        secondary=movie_genre,
        back_populates="movies",
        cascade="all, delete",
        lazy="selectin"
    )
    
    keywords: Mapped[set[KeywordSchema]] = relationship(
        secondary=movie_keyword,
        back_populates="movies",
        cascade="all, delete",
        lazy="selectin"
    )
