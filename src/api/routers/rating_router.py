from fastapi import APIRouter, HTTPException, Query
from pydantic import PositiveInt

from ..schemas import Rating
from ..dependencies import RatingRepo

rating_router = APIRouter(prefix="/ratings", tags=["ratings"])

@rating_router.get("/")
async def get_ratings(
    repo: RatingRepo,
    user: PositiveInt = Query(),
    movie: str = Query()
) -> Rating:
    rating = await repo.get(user, movie)
    if not rating:
        raise HTTPException(
            404,
            "Invalid user or movie"
        )
    return rating

@rating_router.post("/")
async def create_rating(
    repo: RatingRepo,
    rating: Rating
):
    status = await repo.create(rating)
    if status == False:
        raise HTTPException(
            404,
            "Invalid user or movie"
        )
    return True

@rating_router.patch("/")
async def update_rating(
    repo: RatingRepo,
    rating: Rating
) -> bool:
    status = await repo.update(rating)
    if status == False:
        raise HTTPException(
            404,
            "Invalid user or movie"
        )
    return True

@rating_router.delete("/")
async def delete_rating(
    repo: RatingRepo,
    user: PositiveInt = Query(),
    movie: str = Query()
):
    status = await repo.delete(user, movie)
    if status == False:
        raise HTTPException(
            404,
            "Invalid user or movie"
        )
    return True