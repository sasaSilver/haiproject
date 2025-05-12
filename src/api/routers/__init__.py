from .movie_router import movie_router
from .user_router import user_router
from .rating_router import rating_router
from .auth_router import auth_router
from .search_router import search_router
from .recommendations_router import rec_router

routers = [
    movie_router,
    user_router,
    rating_router,
    auth_router,
    search_router,
    rec_router
]
