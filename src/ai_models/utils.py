from sqlalchemy import create_engine, select
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database.models import MovieSchema
from src.database.core import async_session

async def get_movie_titles() -> list[tuple[str, str]]:
    async with async_session() as conn:
        return await conn.execute(select(MovieSchema.id, MovieSchema.title)).all()

async def get_movie_keywords() -> list[tuple[str, list[str]]]:
    async with async_session() as conn:
        movies =  (await conn.execute(
            select(MovieSchema)
            .options(selectinload(MovieSchema.keywords))
        )).scalars().all()
        ids_keywords = [(movie.id, [k.name for k in movie.keywords]) for movie in movies]
        return ids_keywords