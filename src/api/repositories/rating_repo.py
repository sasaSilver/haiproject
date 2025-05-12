from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from .base_repo import BaseRepository
from ..schemas import Rating
from src.database.models import RatingSchema, UserSchema, MovieSchema
from sqlalchemy.orm import selectinload

class RatingRepository(BaseRepository):
    async def get(
        self,
        user_id: int,
        movie_id: str,
    ) -> Rating | None:
        query = (
            select(RatingSchema)
            .where(RatingSchema.user_id == user_id)
            .where(RatingSchema.movie_id == movie_id)
        )
        rating = (await self.db.execute(query)).scalar_one_or_none()
        return rating

    async def create(self, rating: Rating) -> bool:
        rating_obj = RatingSchema(**rating.model_dump())
        user_query = (
            select(UserSchema).
            options(selectinload(UserSchema.ratings)).
            where(UserSchema.id == rating_obj.user_id)
        )
        movie_query = (
            select(MovieSchema).
            options(selectinload(MovieSchema.ratings)).
            where(MovieSchema.id == rating_obj.movie_id)
        )
        user_result = await self.db.execute(user_query)
        movie_result = await self.db.execute(movie_query)
        user = user_result.scalar_one_or_none()
        movie = movie_result.scalar_one_or_none()
        if user is None or movie is None:
            return False
        if user.ratings is None:
            user.ratings = set()
        if movie.ratings is None:
            movie.ratings = set()
        user.ratings.add(rating_obj)
        movie.ratings.add(rating_obj)
        self.db.add(rating_obj)
        try:
            await self.db.commit()
        except IntegrityError:
            return False
        return True

    async def update(self, rating: Rating) -> bool:
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
