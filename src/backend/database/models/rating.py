from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, CheckConstraint

from .base import Base

class RatingSchema(Base):
    __tablename__ = "ratings"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    rating: Mapped[int] = mapped_column(
        CheckConstraint('rating >= 1 AND rating <= 10', name='check_rating_range')
    )

    user: Mapped["UserSchema"] = relationship( # type: ignore
        back_populates="ratings"
    )

    movie: Mapped["MovieSchema"] = relationship( # type: ignore
        back_populates="ratings"
    )
