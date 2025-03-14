from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update, delete
from pydantic import PositiveInt

from src.backend.database.models import *
from ..utils import DBSession
from ..schemas import *

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/")
async def create_user(
    user: UserCreate,
    db: DBSession
) -> UserRead:
    user = UserSchema(**user.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)

@user_router.get("/")
async def get_users(
    db: DBSession,
    skip: PositiveInt = 0,
    limit: PositiveInt = 100
) -> list[UserRead]:
   return list(map(
       lambda user: UserRead.model_validate(user),
       (await db.execute(
           select(UserSchema).offset(skip).limit(limit)
        )).scalars().all()
   ))

@user_router.get("/{user_id}")
async def get_user(
    user_id: PositiveInt,
    db: DBSession
) -> UserRead:
    user = (
        await db.execute(
            select(UserSchema).
            where(UserSchema.id == user_id)
        )
    ).scalar_one_or_none()
    
    if user is None:
        raise HTTPException(422, f"No user with id <{user_id}>")
    
    return UserRead.model_validate(user)

@user_router.patch("/{user_id}")
async def update_user(
    user_id: PositiveInt,
    user: UserUpdate,
    db: DBSession
) -> UserRead:
    updated = (await db.execute(
        update(UserSchema).
        where(UserSchema.id == user_id).
        values(**user.model_dump())
    )).rowcount
    
    if updated == 0:
        raise HTTPException(422, f"No user with id <{user_id}>")
    
    return {"message": f"User with id <{user_id}> updated successfully"}
    
@user_router.delete("/{user_id}")
async def delete_user(
    user_id: PositiveInt,
    db: DBSession
):
    deleted = (await db.execute(
        delete(UserSchema).where(UserSchema.id == user_id)
    )).rowcount
    
    if deleted == 0:
        raise HTTPException(422, f"No user with id <{user_id}>")
    
    return {"message": f"User with id {user_id} deleted successfully"}
