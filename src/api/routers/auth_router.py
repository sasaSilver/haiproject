from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from ..dependencies import AuthRepo
from ..schemas import UserCreate, CurrentUser, Token

auth_router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@auth_router.post("/register")
async def register(
    user: UserCreate,
    repo: AuthRepo
) -> Token:
    token = await repo.register(user)
    if not token:
        raise HTTPException(400, "Username already registered")
    return token


@auth_router.post("/login")
async def login(
    user: UserCreate,
    repo: AuthRepo,
) -> Token:
    token = await repo.login(user.name, user.password)
    if not token:
        raise HTTPException(
            401,
            "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_current_user(
    repo: AuthRepo,
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:
    user = await repo.get_current_user(token)
    if not user:
        raise HTTPException(
            401,
            "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
