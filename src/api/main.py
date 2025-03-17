from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from .routers import routers
from ..config import settings

app = FastAPI(
    title=settings.project_name
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def ping() -> str:
    return Response(content="alive", media_type="text/plain")

for router in routers:
    app.include_router(router)
