from fastapi import APIRouter, HTTPException, Query
from pydantic import PositiveInt

from ..schemas import MovieCreate, MovieRead, MovieUpdate
from ..dependencies import MovieRepo

movie_router = APIRouter(prefix="/movies", tags=["movies"])

@movie_router.post("/")
async def create_movie(
    repo: MovieRepo, 
    movie: MovieCreate
) -> MovieRead:
    return await repo.create(movie)

@movie_router.get("/")
async def get_movies(
    repo: MovieRepo,
    skip: PositiveInt = Query(0),
    limit: PositiveInt = Query(100, le=100)
) -> list[MovieRead]:
    return await repo.get_all(skip, limit)

@movie_router.get("/{movie_id}")
async def get_movie(
    repo: MovieRepo,
    movie_id: PositiveInt
) -> MovieRead:
    movie = await repo.get(movie_id)
    if movie is None:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return movie

@movie_router.patch("/{movie_id}")
async def update_movie(
    repo: MovieRepo,
    movie_id: PositiveInt,
    movie: MovieUpdate,
):
    success = await repo.update(movie_id, movie)
    if success == False:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return {"message": f"Movie with id {movie_id} updated successfully"}

@movie_router.delete("/{movie_id}")
async def delete_movie(
    repo: MovieRepo,
    movie_id: PositiveInt
):
    success = await repo.delete(movie_id)
    if success == False:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return {"message": f"Movie with id {movie_id} deleted successfully"}
