from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from .base_repo import BaseRepository
from ..schemas import Rating, RatingUpdate
from src.database.models import RatingSchema

class RatingRepository(BaseRepository):
    async def get_all(
        self,
        user_id: int | None,
        movie_id: int | None,
        skip: int,
        limit: int
    ) -> list[Rating]:
        query = select(RatingSchema)
        if user_id is not None:
            query = query.where(RatingSchema.user_id == user_id)
        if movie_id is not None:
            query = query.where(RatingSchema.movie_id == movie_id)
        ratings = (await self.db.execute(query.offset(skip).limit(limit))).scalars().all()
        return [Rating.model_validate(rating) for rating in ratings]

    async def create(self, rating: Rating) -> bool:
        rating = RatingSchema(**rating.model_dump())
        self.db.add(rating)
        try:
            await self.db.commit()
        except IntegrityError:
            return False
        return True

    async def update(self, rating: RatingUpdate) -> bool:
        updated = (await self.db.execute(
            update(RatingSchema).
            where(RatingSchema.movie_id == rating.movie_id).
            where(RatingSchema.user_id == rating.user_id).
            values(rating=rating.rating)
        )).rowcount
        return bool(updated)

    async def delete(self, user_id: int, movie_id: int) -> bool:
        deleted = (await self.db.execute(
            delete(RatingSchema).
            where(RatingSchema.user_id == user_id).
            where(RatingSchema.movie_id == movie_id)
        )).rowcount
        return bool(deleted)
