from pydantic import PositiveInt, PositiveFloat
from fastapi import APIRouter, Query, HTTPException
from src.api.dependencies import MovieRepo
from src.ai_models import SearchTitleModel, SearchAiModel
from src.api.schemas import MovieRead

search_router = APIRouter(prefix="/search", tags=["search"])

@search_router.get("/")
async def search(
    movie_repo: MovieRepo,
    ai: bool = Query(False),
    q: str | None = Query(None),
    _and: list[str] | None = Query(None, alias="and"),
    _or: list[str] | None = Query(None, alias="or"),
    _not: list[str] | None = Query(None, alias="not"),
    year: PositiveInt | None = Query(None),
    rating: PositiveFloat | None = Query(None),
    skip: PositiveInt = Query(0),
    limit: PositiveInt = Query(100)
):
    if not q:
        return await movie_repo.get_all(skip, limit)
    movie_ids = SearchAiModel.predict(q.strip()) if ai else SearchTitleModel.predict(q)
    return await movie_repo.get_by_ids(movie_ids, _and, _or, _not, year, rating, skip, limit)