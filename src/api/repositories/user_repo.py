from sqlalchemy import select, update, delete

from .base_repo import BaseRepository
from ..schemas import UserCreate, UserRead, UserUpdate
from src.database.models import UserSchema

class UserRepository(BaseRepository):
    async def create(self, user: UserCreate) -> UserRead:
        user = UserSchema(**user.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return UserRead.model_validate(user)        
    
    async def get_all(self, skip: int, limit: int) -> list[UserRead]:
        return list(map(
            lambda user: UserRead.model_validate(user),
            (await self.db.execute(
                select(UserSchema).
                offset(skip).
                limit(limit)
            )).scalars().all()
        ))
        
    async def get(self, id_or_name: int | str) -> UserRead | None:
        query = select(UserSchema)
        if isinstance(id_or_name, int):
            query = query.where(UserSchema.id == id_or_name)
        else:
            query = query.where(UserSchema.name == id_or_name)
        user = (await self.db.execute(query)).scalar_one_or_none()
        return UserRead.model_validate(user) if user else None
    
    async def update(self, user_id: int, user: UserUpdate) -> bool:
        updated = (await self.db.execute(
            update(UserSchema).
            where(UserSchema.id == user_id).
            values(**user.model_dump())
        )).rowcount
        return bool(updated)
    
    async def delete(self, user_id: int) -> bool:
        deleted = (await self.db.execute(
            delete(UserSchema).
              where(UserSchema.id == user_id)
        )).rowcount
        
        return bool(deleted)
