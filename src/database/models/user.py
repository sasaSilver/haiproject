from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .rating import RatingSchema

class UserSchema(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()    
    
    ratings: Mapped[set[RatingSchema] | None] = relationship(
        back_populates="user", cascade="all, delete"
    )
