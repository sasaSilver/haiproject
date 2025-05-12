from sqlalchemy import select, update, delete, not_, func
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.dialects.postgresql import insert

from src.database.models.genre import GenreSchema

from .base_repo import BaseRepository
from ..schemas import MovieCreate, MovieRead, MovieUpdate
from src.database.models import MovieSchema, KeywordSchema, RatingSchema

class MovieRepository(BaseRepository):
    async def create(self, movie: MovieCreate) -> MovieRead:
        movie = MovieSchema(
            **movie.model_dump(exclude={"genres"}),
            genres = await self._create_genres(movie.genres)
        )
        self.db.add(movie)
        await self.db.commit()
        return MovieRead.model_validate(movie)
    
    async def get(self, movie_id: str) -> MovieRead | None:
        movie = (await self.db.execute(
            select(MovieSchema)
            .options(selectinload(MovieSchema.genres))
            .where(MovieSchema.id == movie_id)
        )).scalar_one_or_none()
        
        return MovieRead.model_validate(movie) if movie else None
    
    async def get_all(
        self,
        skip: int,
        limit: int
    ) -> list[MovieRead]:
        query = select(MovieSchema).options(selectinload(MovieSchema.genres))
        movies = (await self.db.execute(
            query.offset(skip).limit(limit)
        )).scalars().all()
        return [MovieRead.model_validate(movie) for movie in movies]
    
    async def get_by_ids(
        self,
        movie_ids: list[str],
        _and: list[str] | None = None,
        _or: list[str] | None = None,
        _not: list[str] | None = None,
        year: int | None = None,
        rating: float | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[MovieRead]:
        query = (
            select(MovieSchema)
            .options(selectinload(MovieSchema.genres))
            .where(MovieSchema.id.in_(movie_ids))
        )
        if _and:
            for genre in _and:
                genre_alias = aliased(GenreSchema)
                query = query.join(MovieSchema.genres.of_type(genre_alias))
                query = query.where(genre_alias.name == genre)
        if _or:
            query = query.join(MovieSchema.genres).where(GenreSchema.name.in_(_or))
        if _not:
            query = query.where(not_(MovieSchema.genres.any(GenreSchema.name.in_(_not))))
        if year:
            query = query.where(MovieSchema.year == year)
        if rating:
            query = query.where(MovieSchema.vote_average >= rating)
            
        movies = (await self.db.execute(
            query.offset(skip).limit(limit)
        )).scalars().all()
        
        return [MovieRead.model_validate(movie) for movie in movies]

    async def update(self, movie_id: str, movie: MovieUpdate) -> bool:
        update_movie = movie.model_dump(exclude_unset=True)
        updated = (await self.db.execute(
            update(MovieSchema).
            where(MovieSchema.id == movie_id).
            values(**update_movie)
        )).rowcount
        
        return bool(updated)

    async def delete(self, movie_id: str) -> bool:
        deleted = (await self.db.execute(
            delete(MovieSchema).where(MovieSchema.id == movie_id)
        )).rowcount
        
        return bool(deleted)
    
    async def _create_genres(
        self,
        genre_names: set[str] | None
    ) -> set[KeywordSchema]:
        if not genre_names:
            return set()
        
        new_genres = (await self.db.execute(
            insert(KeywordSchema).
            values([{"name": n} for n in genre_names]).
            on_conflict_do_nothing(index_elements=["name"]).
            returning(KeywordSchema)
        )).scalars().all()
        
        existing = (await self.db.execute(
            select(KeywordSchema).
            where(KeywordSchema.name.in_(genre_names))
        )).scalars().all()
        
        return set(new_genres + existing)

    async def get_popular(self, skip: int, limit: int) -> list[MovieRead]:
        query = (
            select(MovieSchema).
            outerjoin(RatingSchema).
            group_by(MovieSchema.id).
            order_by(func.avg(RatingSchema.rating).desc()).
            options(selectinload(MovieSchema.genres)).
            offset(skip).
            limit(limit)
        )
        
        movies = (await self.db.execute(query)).scalars().all()
        return [MovieRead.model_validate(movie) for movie in movies]
