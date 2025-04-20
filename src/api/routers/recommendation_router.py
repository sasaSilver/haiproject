from fastapi import APIRouter
import numpy as np

from src.api.schemas.rating import Rating

from ..schemas import MovieRead
from ..dependencies import MovieRepo, RatingRepo, UserRepo
from src.database.models import RatingSchema

recommendation_router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

def calculate_user_similarity(user1_ratings: list[RatingSchema], user2_ratings: list[RatingSchema]) -> float:
    """Calculate similarity between two users based on their ratings"""
    # Create dictionaries of movie_id -> rating for both users
    user1_dict = {r.movie_id: r.rating for r in user1_ratings}
    user2_dict = {r.movie_id: r.rating for r in user2_ratings}
    
    # Find common movies
    common_movies = set(user1_dict.keys()) & set(user2_dict.keys())
    
    if not common_movies:
        return 0.0
    
    # Calculate Pearson correlation
    x = [user1_dict[movie_id] for movie_id in common_movies]
    y = [user2_dict[movie_id] for movie_id in common_movies]
    
    if len(x) < 2:
        return 0.0
    
    correlation = np.corrcoef(x, y)[0, 1]
    return correlation if not np.isnan(correlation) else 0.0

@recommendation_router.get("/user/{user_id}")
async def get_user_recommendations(
    user_id: int,
    movie_repo: MovieRepo,
    rating_repo: RatingRepo,
    user_repo: UserRepo,
    limit: int = 10
) -> list[MovieRead]:
    # Get all ratings
    all_ratings: list[Rating] = await rating_repo.get_all()
    
    # Get current user's ratings
    user_ratings = [r for r in all_ratings if r.user_id == user_id]
    
    if not user_ratings:
        # If user has no ratings, return popular movies
        return await movie_repo.get_popular(limit)
    
    # Calculate similarities with other users
    user_similarities = {}
    for rating in all_ratings:
        if rating.user_id != user_id:
            other_user_ratings = [r for r in all_ratings if r.user_id == rating.user_id]
            similarity = calculate_user_similarity(user_ratings, other_user_ratings)
            user_similarities[rating.user_id] = similarity
    
    # Get movies rated by similar users that the current user hasn't rated
    user_movies = {r.movie_id for r in user_ratings}
    movie_scores = {}
    
    for rating in all_ratings:
        if rating.user_id != user_id and rating.movie_id not in user_movies:
            similarity = user_similarities.get(rating.user_id, 0)
            if rating.movie_id not in movie_scores:
                movie_scores[rating.movie_id] = 0
            movie_scores[rating.movie_id] += similarity * rating.rating
    
    # Sort movies by score and get top recommendations
    recommended_movie_ids = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
    recommended_movies = []
    
    for movie_id, _ in recommended_movie_ids:
        movie = await movie_repo.get(movie_id)
        if movie:
            recommended_movies.append(movie)
    
    return recommended_movies 