from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, update, delete, not_
from sqlalchemy.orm import selectinload, aliased

from src.backend.database.models import *
from ..schemas import *
from ..utils import DBSession, create_genres, Lowercase

movie_router = APIRouter(prefix="/movies", tags=["movies"])

def movie_to_pydantic(movie: MovieSchema) -> Movie:
    return Movie(
        id=movie.id,
        title=movie.title,
        duration=movie.duration,
        year=movie.year,
        genres=[g.name for g in movie.genres]
    )

@movie_router.post("/")
async def create_movie(
    db: DBSession, 
    movie: MovieCreate
) -> Movie:
    movie: MovieSchema = MovieSchema(
        title=movie.title,
        duration=movie.duration,
        year=movie.year,
        genres=await create_genres(db, movie.genres)
    )
    db.add(movie)
    await db.commit()
    return movie_to_pydantic(movie)

@movie_router.get("/")
async def get_movies(
    db: DBSession,
    _and: list[Lowercase] | None = Query(None, alias="and"),
    _or: list[Lowercase] | None = Query(None, alias="or"),
    _not: list[Lowercase] | None = Query(None, alias="not"),
    skip: int = 0,
    limit: int = 100
) -> list[Movie]:
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
    
    movies = (await db.execute(
        query.offset(skip).limit(limit)
    )).scalars().all()
    
    return [movie_to_pydantic(movie) for movie in movies]

@movie_router.get("/{movie_id}")
async def get_movie(
    movie_id: int,
    db: DBSession
) -> Movie:
    movie = (
        await db.execute(
            select(MovieSchema).
            options(
                selectinload(MovieSchema.genres),
            ).
            where(MovieSchema.id == movie_id)
        )
    ).scalar_one_or_none()
    if movie is None:
        raise HTTPException(422, f"No movie with id <{movie_id}>")
    return movie_to_pydantic(movie)

@movie_router.patch("/{movie_id}")
async def update_movie(
    movie_id: int, movie: MovieUpdate, db: DBSession
):
    updated = (await db.execute(
        update(MovieSchema).
        where(MovieSchema.id == movie_id).
        values(**movie.model_dump())
    )).rowcount
    
    if updated == 0:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    
    return {"message": f"Movie with id {movie_id} updated successfully"}

@movie_router.delete("/{movie_id}")
async def delete_movie(
    movie_id: int, db: DBSession
):
    deleted = (await db.execute(
        delete(MovieSchema).where(MovieSchema.id == movie_id)
    )).rowcount
    if deleted == 0:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return {"message": f"Movie with id {movie_id} deleted successfully"}
