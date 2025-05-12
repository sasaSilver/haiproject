from fastapi import APIRouter, HTTPException

from ..schemas import MovieCreate, MovieRead, MovieUpdate
from ..dependencies import MovieRepo

movie_router = APIRouter(prefix="/movies", tags=["movies"])

@movie_router.post("/")
async def create_movie(
    repo: MovieRepo, 
    movie: MovieCreate
) -> MovieRead:
    return await repo.create(movie)

@movie_router.get("/{movie_id}")
async def get_movie(
    repo: MovieRepo,
    movie_id: str
) -> MovieRead:
    movie = await repo.get(movie_id)
    if movie is None:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return movie


@movie_router.patch("/{movie_id}")
async def update_movie(
    repo: MovieRepo,
    movie_id: str,
    movie: MovieUpdate,
):
    success = await repo.update(movie_id, movie)
    if success == False:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return True

@movie_router.delete("/{movie_id}")
async def delete_movie(
    repo: MovieRepo,
    movie_id: str
):
    success = await repo.delete(movie_id)
    if success == False:
        raise HTTPException(404, f"No movie with id <{movie_id}>")
    return True
