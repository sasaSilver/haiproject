from fastapi import APIRouter, HTTPException, Query
from pydantic import PositiveInt

from ..schemas import Rating, RatingUpdate
from ..dependencies import RatingRepo

rating_router = APIRouter(prefix="/ratings", tags=["ratings"])

@rating_router.get("/")
async def get_ratings(
    repo: RatingRepo,
    user: PositiveInt | None = None,
    movie: PositiveInt | None = None,
    skip: PositiveInt = Query(0),
    limit: PositiveInt = Query(100, le=100)
) -> list[Rating]:
    return await repo.get_all(user, movie, skip, limit)

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
    updated = await repo.update(rating)
    if not updated:
        raise HTTPException(404, f"No rating for movie <{rating.movie_id}> from user <{rating.user_id}>")
    return {"message": f"Rating for movie <{rating.movie_id}> from user <{rating.user_id}> updated successfully"}

@rating_router.delete("/")
async def delete_rating(
    repo: RatingRepo,
    user: PositiveInt,
    movie: PositiveInt
):
    deleted = await repo.delete(user, movie)
    if not deleted:
        raise HTTPException(404, f"No movie with user id <{user}> and movie id <{movie}>")
    return {"message": f"Deleted rating by user <{user}> to movie <{movie}>"}
