import requests
from typing import List, Dict
import random

BASE_URL = "http://localhost:8000"

def create_test_user(name: str) -> Dict:
    """Create a test user and return their data"""
    response = requests.post(f"{BASE_URL}/users/", json={
        "name": name,
        "email": f"{name.lower()}@test.com",
        "password": "test123",
        "gender": random.choice(["male", "female", "other"]),
        "country": random.choice(["USA", "UK", "Canada", "Australia", "Germany"])
    })
    assert response.status_code == 200
    return response.json()

def create_test_movie(title: str, genres: List[str]) -> Dict:
    """Create a test movie and return its data"""
    response = requests.post(f"{BASE_URL}/movies/", json={
        "title": title,
        "image": "https://example.com/image.jpg",
        "duration": random.randint(5400, 7200),  # 90-120 minutes in seconds
        "year": random.randint(2000, 2024),
        "genres": genres
    })
    assert response.status_code == 200
    return response.json()

def create_test_rating(user_id: int, movie_id: int, rating: int) -> Dict:
    """Create a test rating and return its data"""
    response = requests.post(f"{BASE_URL}/ratings/", json={
        "user_id": user_id,
        "movie_id": movie_id,
        "rating": rating
    })
    assert response.status_code == 200
    return response.json()

def test_recommendation_system():
    # Create test users
    users = []
    for name in ["Alice", "Bob", "Charlie", "David", "Eve"]:
        users.append(create_test_user(name))
    
    # Create test movies with different genres
    movies = []
    genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Romance"]
    
    # Create 10 movies with random genres
    for i in range(10):
        movie_genres = random.sample(genres, random.randint(1, 3))
        movies.append(create_test_movie(f"Movie {i+1}", movie_genres))
    
    # Create ratings with some patterns to test recommendations
    # Alice likes Action and Sci-Fi movies
    for movie in movies:
        if any(genre in ["Action", "Sci-Fi"] for genre in movie["genres"]):
            create_test_rating(users[0]["id"], movie["id"], random.randint(8, 10))
        else:
            create_test_rating(users[0]["id"], movie["id"], random.randint(1, 5))
    
    # Bob likes Comedy and Romance movies
    for movie in movies:
        if any(genre in ["Comedy", "Romance"] for genre in movie["genres"]):
            create_test_rating(users[1]["id"], movie["id"], random.randint(8, 10))
        else:
            create_test_rating(users[1]["id"], movie["id"], random.randint(1, 5))
    
    # Charlie likes Drama movies
    for movie in movies:
        if "Drama" in movie["genres"]:
            create_test_rating(users[2]["id"], movie["id"], random.randint(8, 10))
        else:
            create_test_rating(users[2]["id"], movie["id"], random.randint(1, 5))
    
    # David and Eve have random ratings
    for user in [users[3], users[4]]:
        for movie in movies:
            create_test_rating(user["id"], movie["id"], random.randint(1, 10))
    
    # Test recommendations for Alice (should prefer Action and Sci-Fi)
    response = requests.get(f"{BASE_URL}/recommendations/user/{users[0]['id']}")
    assert response.status_code == 200
    alice_recommendations = response.json()
    print("\nAlice's recommendations:")
    for movie in alice_recommendations:
        print(f"- {movie['title']} (Genres: {', '.join(genre['name'] for genre in movie['genres'])})")
    
    # Test recommendations for Bob (should prefer Comedy and Romance)
    response = requests.get(f"{BASE_URL}/recommendations/user/{users[1]['id']}")
    assert response.status_code == 200
    bob_recommendations = response.json()
    print("\nBob's recommendations:")
    for movie in bob_recommendations:
        print(f"- {movie['title']} (Genres: {', '.join(genre['name'] for genre in movie['genres'])})")
    
    # Test recommendations for Charlie (should prefer Drama)
    response = requests.get(f"{BASE_URL}/recommendations/user/{users[2]['id']}")
    assert response.status_code == 200
    charlie_recommendations = response.json()
    print("\nCharlie's recommendations:")
    for movie in charlie_recommendations:
        print(f"- {movie['title']} (Genres: {', '.join(genre['name'] for genre in movie['genres'])})")
    
    # Test recommendations for a new user (should get popular movies)
    new_user = create_test_user("NewUser")
    response = requests.get(f"{BASE_URL}/recommendations/user/{new_user['id']}")
    assert response.status_code == 200
    new_user_recommendations = response.json()
    print("\nNew user's recommendations (popular movies):")
    for movie in new_user_recommendations:
        print(f"- {movie['title']} (Genres: {', '.join(genre['name'] for genre in movie['genres'])})")

if __name__ == "__main__":
    test_recommendation_system() 