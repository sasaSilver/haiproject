from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import PositiveInt

from ..schemas import UserCreate, UserRead, UserUpdate, CurrentUser, Rating
from ..dependencies import UserRepo, RatingRepo
from .auth_router import get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/me")
async def get_current_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    return current_user

@user_router.patch("/me")
async def update_current_user(
    repo: UserRepo,
    name: str,
    current_user: CurrentUser = Depends(get_current_user)
) -> bool:
    return repo.update(current_user.id, UserUpdate(name=name))

@user_router.post("/me/rate/")
async def rate_movie(
    rating_repo: RatingRepo,
    movie_id: PositiveInt = Query(),
    rating: float = Query(),
    current_user: CurrentUser = Depends(get_current_user),
) -> bool:
    rating = Rating(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=rating
    )
    result = await rating_repo.create(rating)
    if result == False:
        raise HTTPException(status_code=400, detail="Rating could not be processed")
    return True

@user_router.post("/", response_model=UserRead)
async def create_user(
    repo: UserRepo,
    user: UserCreate
) -> UserRead:
    existing_user = await repo.get(user.name)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return await repo.create(user)

@user_router.get("/", response_model=list[UserRead])
async def get_users(
    repo: UserRepo,
    skip: PositiveInt = Query(0),
    limit: PositiveInt = Query(100, le=100)
) -> list[UserRead]:
   return await repo.get_all(skip, limit)

@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    repo: UserRepo,
    user_id: PositiveInt
) -> UserRead:
    user = await repo.get(user_id)
    if user is None:
        raise HTTPException(404, detail="User not found")
    return user

@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    repo: UserRepo,
    user_id: PositiveInt,
    user: UserUpdate
) -> UserRead:
    status = await repo.update(user_id, user)
    if status == False:
        raise HTTPException(422, f"No user with id <{user_id}>")
    return await repo.get(user_id)
    
@user_router.delete("/{user_id}")
async def delete_user(
    repo: UserRepo,
    user_id: PositiveInt
):
    status = await repo.delete(user_id)
    if status == False:
        raise HTTPException(422, f"No user with id <{user_id}>")
    return True
