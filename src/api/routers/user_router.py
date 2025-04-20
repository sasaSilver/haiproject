from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import PositiveInt

from ..schemas import UserCreate, UserRead, UserUpdate
from ..dependencies import UserRepo
from .auth_router import get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/me")
async def get_current_user_info(
    current_user: UserRead = Depends(get_current_user)
) -> UserRead:
    return current_user

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
    skip: PositiveInt = 0,
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