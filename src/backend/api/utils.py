from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.database import get_db

DBSession = Annotated[AsyncSession, Depends(get_db)]

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert # pgsql-specific insert. supports on_conflict_do_nothing
from src.backend.database.models import *
from .schemas import *

async def create_genres(
        db: DBSession,
        genre_names: set[str | None]
) -> set[GenreSchema]:
    if not genre_names:
        return set()
    
    query = (
        insert(GenreSchema).
        values([{"name": n} for n in genre_names]).
        on_conflict_do_nothing(index_elements=["name"]).
        returning(GenreSchema)
    )
    
    new_genres = (await db.execute(query)).scalars().all()
    
    existing = (await db.execute(
        select(GenreSchema).
        where(GenreSchema.name.in_(genre_names))
    )).scalars().all()
    
    return set(new_genres + existing)

from pydantic.types import StringConstraints

Alphabetic = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]+$")]
Lowercase = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]+$", to_lower=True)]

def movie_to_pydantic(movie: MovieSchema):
    return Movie(
        id=movie.id,
        title=movie.title,
        duration=movie.duration,
        year=movie.year,
        genres=[g.name for g in movie.genres]
    )
