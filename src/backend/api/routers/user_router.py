from fastapi import APIRouter, HTTPException, Query
from pydantic import PositiveInt

from ..schemas import UserCreate, UserRead, UserUpdate
from ..dependencies import UserRepo

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/")
async def create_user(
    repo: UserRepo,
    user: UserCreate
) -> UserRead:
    return await repo.create(user)

@user_router.get("/")
async def get_users(
    repo: UserRepo,
    skip: PositiveInt = Query(0),
    limit: PositiveInt = Query(100, le=100)
) -> list[UserRead]:
   return await repo.get_all(skip, limit)

@user_router.get("/{user_id}")
async def get_user(
    repo: UserRepo,
    user_id: PositiveInt
) -> UserRead:
    user = repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.patch("/{user_id}")
async def update_user(
    repo: UserRepo,
    user_id: PositiveInt,
    user: UserUpdate
) -> UserRead:
    status = await repo.update(user_id, UserUpdate)
    if status == False:
        raise HTTPException(422, f"No user with id <{user_id}>")
    
@user_router.delete("/{user_id}")
async def delete_user(
    repo: UserRepo,
    user_id: PositiveInt
):
    status = repo.delete(user_id)
    if status == False:
        raise HTTPException(422, f"No user with id <{user_id}>")
