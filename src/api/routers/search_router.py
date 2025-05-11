from fastapi import APIRouter, Query, HTTPException
from src.api.dependencies import MovieRepo
from src.ai_models import SearchTitleModel, SearchKeywordsModel

search_router = APIRouter(prefix="/search", tags=["search"])

@search_router.get("/")
async def search(
    movie_repo: MovieRepo,
    ai: bool = Query(False),
    q: str | None = Query(None),
):
    if not q:
        raise HTTPException(
            401,
            "No query provided"
        )
    q = q.strip()
    if not ai:
        movie_ids = SearchTitleModel.predict(q)
        for id in movie_ids:
            movie_repo.get