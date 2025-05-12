from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database.models import MovieSchema, RatingSchema
from src.database.core import async_session

async def get_movie_titles() -> list[tuple[str, str]]:
    async with async_session() as session:
        result = await session.execute(select(MovieSchema.id, MovieSchema.title))
        return result.all()

async def get_movie_keywords() -> list[tuple[str, list[str]]]:
    async with async_session() as session:
        result = await session.execute(
            select(MovieSchema)
            .options(
                selectinload(MovieSchema.keywords),
                selectinload(MovieSchema.genres)
            )
        )
        movies = result.scalars().all()
        ids_keywords = [
            (movie.id, [k.name for k in movie.keywords] + [g.name for g in movie.genres] + [movie.title])
            for movie in movies
        ]
        return ids_keywords

async def get_ratings() -> list[RatingSchema]:
    async with async_session() as session:
        result = (await session.execute(
             select(RatingSchema)
        )).scalars().all()
        return result

async def get_movies() -> list[MovieSchema]:
    async with async_session() as session:
        result = (await session.execute(
            select(MovieSchema).options(selectinload(MovieSchema.genres))
        )).scalars().all()
        return result

class TrainException(Exception):
    def __init__(self, *args):
        super().__init__(*args)