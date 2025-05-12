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
    try:
        SearchTitleModel.load()
        print("Using cached SearchTitleModel")
    except ai_utils.TrainException:
        print("Training SearchTitleModel")
        SearchTitleModel.train(await ai_utils.get_movie_titles())
    try:
        SearchAiModel.load()
        print("Using cached SearchKeywordsModel")
    except ai_utils.TrainException:
        print("Training SearchKeywordsModel")
        SearchAiModel.train(await ai_utils.get_movie_keywords())
    try:
        CollaborativeFilteringModel.load()
        print("Using cached CollaborativeFilteringModel")
    except ai_utils.TrainException:
        print("Training CollaborativeFilteringModel")
        CollaborativeFilteringModel.train(await ai_utils.get_ratings())
    try:
        ContentFilteringModel.load()
        print("Using cached ContentFilteringModel")
    except ai_utils.TrainException:
        print("Training ContentFilteringModel")
        ContentFilteringModel.train(await ai_utils.get_movies())
    yield

app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan
)

origins = [
    "http://localhost:3000"
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
