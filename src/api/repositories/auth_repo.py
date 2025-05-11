import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base_repo import BaseRepository
from ..schemas import UserCreate, CurrentUser, Token, TokenData
from src.database.models import UserSchema
from src.database.models.rating import RatingSchema
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthRepository(BaseRepository):
    async def login(self, name: str, password: str) -> Token | None:
        query = select(UserSchema).where(UserSchema.name == name)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not pwd_context.verify(password, user.password):
            return None
        access_token = self._create_access_token(data={"sub": user.name})
        return Token(access_token=access_token, token_type="bearer", user_id=user.id)
    
    async def register(self, user: UserCreate) -> Token | None:
        query = select(UserSchema).where(UserSchema.name == user.name)
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            return None
        
        hashed_password = pwd_context.hash(user.password)
        new_user = UserSchema(
            name=user.name,
            password=hashed_password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        access_token = self._create_access_token(data={"sub": new_user.name})
        return Token(access_token=access_token, token_type="bearer", user_id=new_user.id)
    
    def _create_access_token(self, data: dict) -> str:
        expire = datetime.now() + timedelta(days=settings.access_token_expire_d)
        data.update({"exp": expire})
        encoded_jwt = jwt.encode(data, settings.secret, algorithm=settings.algorithm)
        return encoded_jwt
    
    async def get_current_user(self, token: str) -> CurrentUser | None:
        try:
            payload: dict = jwt.decode(token, settings.secret, algorithms=[settings.algorithm])
            name: str | None = payload.get("sub")
            if name is None:
                return None
            token_data = TokenData(name=name)
        except (InvalidTokenError, ExpiredSignatureError):
            return None
        query = select(UserSchema).options(
            selectinload(UserSchema.ratings).selectinload(RatingSchema.movie)
        ).where(UserSchema.name == token_data.name)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        try:
            user = CurrentUser.model_validate(user)
        except ValidationError as e:
            print(e.json())
        return user
    
