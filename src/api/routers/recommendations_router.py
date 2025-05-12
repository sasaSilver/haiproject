from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.api.schemas.movie import MovieRead
from src.api.dependencies import MovieRepo
from src.ai_models import CollaborativeFilteringModel, ContentFilteringModel
from src.database.core import get_db

rec_router = APIRouter(prefix="/recommend", tags=["recommendations"])

@rec_router.get("/")
async def get_recommendations(
    repo: MovieRepo,
    movie: str | None = Query(None),
    user: int | None = Query(None)
) -> list[MovieRead]:
    if movie:
        movie_ids = ContentFilteringModel.predict(movie)
    elif user:
        movie_ids = CollaborativeFilteringModel.predict(user)
    return await repo.get_by_ids(movie_ids)

@rec_router.get("/movies")
async def get_best_movies(
    db: AsyncSession = Depends(get_db)
) -> list[MovieRead]:
    result = await db.execute(text("SELECT * FROM get_best_movies()"))
    movies = result.scalars().all()
    return [MovieRead.model_validate(movie) for movie in movies]
    