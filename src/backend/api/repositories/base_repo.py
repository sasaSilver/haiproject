from fastapi import Depends
from src.backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @classmethod
    def get_repo(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
