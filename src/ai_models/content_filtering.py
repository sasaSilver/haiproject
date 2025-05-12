from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .base import ModelBase
from .utils import TrainException
from src.database.models import MovieSchema

class ContentFilteringModel(ModelBase, model_cache_path="content_filtering_cache.pkl"):
    model = None
    id_map = None
    matrix = None

    @classmethod
    def load(cls):
        if cache := cls.load_cache():
            cls.model = cache["model"]
            cls.matrix = cache["matrix"]
            cls.id_map = cache["id_map"]
            return
        raise TrainException(f"{cls.__name__} missing cache.")

    @classmethod
    def train(cls, movies: list[MovieSchema]):
        cls.id_map = {arr_id: movie.id for arr_id, movie in enumerate(movies)}
        combined_features = []
        for movie in movies:
            genres = ", ".join([genre.name for genre in movie.genres]) if movie.genres else ""
            keywords = " ".join([kw.name for kw in movie.keywords]) if movie.keywords else ""
            feature_text = " ".join([
                movie.title,
                str(movie.year),
                genres,
                keywords,
                movie.description,
                f"popularity_{movie.popularity}",
                f"rating_{int(movie.vote_average)}",
            ]).lower()
            combined_features.append(feature_text)
        cls.model = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=3,
            max_features=5000,
            analyzer='word'
        )
        cls.matrix = cls.model.fit_transform(combined_features)
        cls.dump_cache({
            "matrix": cls.matrix,
            "model": cls.model,
            "id_map": cls.id_map
        })

    @classmethod
    def predict(cls, target_movie_id: str, top_n: int = 10) -> list[str]:
        if any([cls.id_map is None and cls.model is None and cls.matrix is None]):
            raise TrainException("Model not trained or loaded")
        reverse_id_map = {v: k for k, v in cls.id_map.items()}
        if target_movie_id not in reverse_id_map:
            return []
        target_idx = reverse_id_map[target_movie_id]
        similarity_scores = cosine_similarity(cls.matrix[target_idx:target_idx+1], cls.matrix).flatten()
        similar_indices = np.argsort(-similarity_scores)[1:top_n+1]
        return [cls.id_map[i] for i in similar_indices if similarity_scores[i] > 0]