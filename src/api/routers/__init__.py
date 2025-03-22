from .movie_router import movie_router
from .user_router import user_router
from .rating_router import rating_router
from .recommendation_router import recommendation_router

routers = [
    movie_router,
    user_router,
    rating_router,
    recommendation_router
]
