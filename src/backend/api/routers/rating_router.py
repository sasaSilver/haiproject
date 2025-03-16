from fastapi import APIRouter, HTTPException, Query
from pydantic import PositiveInt

from ..schemas import Rating, RatingUpdate
from ..dependencies import RatingRepo

rating_router = APIRouter(prefix="/ratings", tags=["ratings"])

@rating_router.get("/")
async def get_ratings(
    repo: RatingRepo,
    user_id: PositiveInt | None = Query(None, alias="user"),
    movie_id: PositiveInt | None = Query(None, alias="movie"),
    skip: PositiveInt = Query(0),
    limit: PositiveInt = Query(100, le=100)
) -> list[Rating]:
    return await repo.get_all(user_id, movie_id, skip, limit)

@rating_router.post("/")
async def create_rating(
    repo: RatingRepo,
    rating: Rating
) -> Rating:
    return await repo.create(rating)

@rating_router.patch("/")
async def update_rating(
    repo: RatingRepo,
    rating: RatingUpdate
) -> dict:
    status = await repo.update(rating)
    if status == False:
        raise HTTPException(404, f"No rating for movie <{rating.movie_id}> from user <{rating.user_id}>")

@rating_router.delete("/")
async def delete_rating(
    repo: RatingRepo,
    user_id: PositiveInt | None = Query(None, alias="user"),
    movie_id: PositiveInt | None = Query(None, alias="movie")
):
    status = await repo.delete(user_id, movie_id)
    if status == False:
        raise HTTPException(404, f"No movie with user id <{user_id}> and movie id <{movie_id}>")
