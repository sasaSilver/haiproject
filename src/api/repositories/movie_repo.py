from sqlalchemy import select, update, delete, not_, func
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.dialects.postgresql import insert

from .base_repo import BaseRepository
from ..schemas import MovieCreate, MovieRead, MovieUpdate
from src.database.models import MovieSchema, GenreSchema, RatingSchema

class MovieRepository(BaseRepository):
    async def create(self, movie: MovieCreate) -> MovieRead:
        movie = MovieSchema(
            **movie.model_dump(exclude={"genres"}),
            genres = await self._create_genres(movie.genres)
        )
        self.db.add(movie)
        await self.db.commit()
        return MovieRead.model_validate(movie)

    async def get_all(
            self,
            _and: list[str] | None,
            _or: list[str] | None,
            _not: list[str] | None,
            skip = 0,
            limit = 100
    ) -> list[MovieRead]:
        query = select(MovieSchema).options(selectinload(MovieSchema.genres))
        if _and:
            for genre in _and:
                genre_alias = aliased(GenreSchema)
                query = query.join(MovieSchema.genres.of_type(genre_alias))
                query = query.where(genre_alias.name == genre)
        if _or:
            query = query.join(MovieSchema.genres).where(GenreSchema.name.in_(_or))
        if _not:
            query = query.where(not_(MovieSchema.genres.any(GenreSchema.name.in_(_not))))
            
        query = query.group_by(MovieSchema.id)
        movies = (await self.db.execute(
            query.offset(skip).limit(limit)
        )).scalars().all()
        
        return [MovieRead.model_validate(movie) for movie in movies]
    
    async def get(self, movie_id: int) -> MovieRead | None:
        movie = (await self.db.execute(
            select(MovieSchema).
            options(
                selectinload(MovieSchema.genres),
            ).
            where(MovieSchema.id == movie_id)
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
    
    async def _create_genres(
        self,
        genre_names: set[str] | None
    ) -> set[GenreSchema]:
        if not genre_names:
            return set()
        
        new_genres = (await self.db.execute(
            insert(GenreSchema).
            values([{"name": n} for n in genre_names]).
            on_conflict_do_nothing(index_elements=["name"]). # genres have unique constraint
            returning(GenreSchema)
        )).scalars().all()
        
        existing = (await self.db.execute(
            select(GenreSchema).
            where(GenreSchema.name.in_(genre_names))
        )).scalars().all()
        
        return set(new_genres + existing)

    async def get_popular(self, limit: int = 10) -> list[MovieRead]:
        query = (
            select(MovieSchema)
            .outerjoin(RatingSchema)
            .group_by(MovieSchema.id)
            .order_by(func.avg(RatingSchema.rating).desc())
            .options(selectinload(MovieSchema.genres))
            .limit(limit)
        )
        
        movies = (await self.db.execute(query)).scalars().all()
        return [MovieRead.model_validate(movie) for movie in movies]
