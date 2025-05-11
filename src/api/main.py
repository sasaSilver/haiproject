from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import routers
from ..config import settings

from src.database.core import create_tables, create_db_utils
import src.ai_models.utils as ai_utils
from src.ai_models import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await create_db_utils()
    SearchTitleModel.train(ai_utils.get_movie_titles())
    yield

app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    # frontend url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def ping():
    return "yo"

for router in routers:
    app.include_router(router)
