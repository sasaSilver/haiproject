from sqlalchemy import Column, ForeignKey, Table, Text
from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import Base

movie_keyword = Table(
    'movie_keywords',
    Base.metadata,
    Column("movie_id", Text, ForeignKey('movies.id', ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", Text, ForeignKey('keywords.id', ondelete="CASCADE"), primary_key=True)
)

class KeywordSchema(Base):
    __tablename__ = "keywords"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    
    movies: Mapped[set["MovieSchema"]] = relationship( # type: ignore
        secondary=movie_keyword,
        back_populates="keywords",
        lazy="selectin"
    )
