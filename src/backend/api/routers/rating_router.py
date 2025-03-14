from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from src.backend.database.models import *
from ..schemas import *
from ..utils import DBSession

rating_router = APIRouter(prefix="/ratings", tags=["ratings"])

@rating_router.get("/")
async def get_ratings(
    db: DBSession,
    user: int | None = None,
    movie: int | None = None,
    skip: int = 0,
    limit: int = 100
) -> list[Rating]:
    query = select(RatingSchema)
    if user is not None:
        query = query.where(RatingSchema.user_id == user)
    if movie is not None:
        query = query.where(RatingSchema.movie_id == movie)
    return list(
        (await db.execute(
            query.offset(skip).limit(limit)
        )).scalars().all()
    )

@rating_router.post("/")
async def create_rating(
    db: DBSession,
    rating: Rating
) -> Rating:
    rating = RatingSchema(**rating.model_dump())
    db.add(rating)
    try:
        await db.flush()
    except IntegrityError as e:
        raise HTTPException(
            404,
            f"No movie or user with ids <{rating.movie_id}> and <{rating.user_id}>"
        )
    return Rating.model_validate(rating)

@rating_router.patch("/")
async def update_rating(
    db: DBSession,
    rating: RatingUpdate
) -> Rating:
    updated = (await db.execute(
        update(RatingSchema).
        where(RatingSchema.movie_id == rating.movie_id).
        where(RatingSchema.user_id == rating.user_id).
        values(rating = rating.rating)
    )).rowcount
    if updated == 0:
        raise HTTPException(
            404,
            f"No rating for movie <{rating.movie_id}> from user <{rating.user_id}>"
        )
    return {"message": f"Rating for movie <{rating.movie_id}>\
                         from user <{rating.user_id}> updated successfully"}

@rating_router.delete("/")
async def delete_rating(
    db: DBSession,
    user: int | None = None,
    movie: int | None = None
):
    deleted = (await db.execute(
        delete(RatingSchema).
        where(RatingSchema.user_id == user).
        where(RatingSchema.movie_id == movie)
    )).rowcount
    if deleted == 0:
        raise HTTPException(404, f"No movie with user id <{user}> and movie id <{movie}>")
    return {"message": f"Deleted rating by user <{user}> to movie <{movie}>"}
