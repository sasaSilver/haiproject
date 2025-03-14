from .base_repo import BaseRepository
from sqlalchemy import select, update, delete
from ..schemas import MovieCreate, MovieRead, MovieUpdate
from src.backend.database.models import MovieSchema

class MovieRepository(BaseRepository):
    async def create(self, movie: MovieCreate) -> MovieRead:
        movie = MovieSchema(**movie.model_dump())
        self.db.add(movie)
        await self.db.commit()
        return MovieRead.model_validate(movie)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[MovieRead]:
        movies = (await self.db.execute(
            select(MovieSchema).offset(skip).limit(limit)
        )).scalars().all()
        return [MovieRead.model_validate(movie) for movie in movies]

    async def get(self, movie_id: int) -> MovieRead | None:
        movie = (await self.db.execute(
            select(MovieSchema).where(MovieSchema.id == movie_id)
        )).scalar_one_or_none()
        return MovieRead.model_validate(movie) if movie else None

    async def update(self, movie_id: int, movie: MovieUpdate) -> bool:
        updated = (await self.db.execute(
            update(MovieSchema).where(MovieSchema.id == movie_id).values(**movie.model_dump())
        )).rowcount
        return bool(updated)

    async def delete(self, movie_id: int) -> bool:
        deleted = (await self.db.execute(
            delete(MovieSchema).where(MovieSchema.id == movie_id)
        )).rowcount
        return bool(deleted)
