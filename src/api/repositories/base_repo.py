from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @classmethod
    def get_repo(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
