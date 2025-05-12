from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .base import ModelBase
from .utils import TrainException

class SearchTitleModel(ModelBase, model_cache_path="search_title_cache.pkl"):
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
    def train(cls, movie_ids_titles: list[tuple[str, str]]):
        cls.id_map = {arr_id: id_title[0] for arr_id, id_title in enumerate(movie_ids_titles)}
        movie_titles = [id_title[1] for id_title in movie_ids_titles]
        cls.model = TfidfVectorizer(
            strip_accents="ascii",
            ngram_range=(1, 2)
        ).fit(movie_titles)
        cls.matrix = cls.model.transform(movie_titles)
        cls.dump_cache({
            "matrix": cls.matrix,
            "model": cls.model,
            "id_map": cls.id_map
        })

    @classmethod
    def predict(cls, movie_title: str, top_n: int = 5) -> list[str]:
        if any([cls.id_map is None and cls.model is None and cls.matrix is None]):
            raise TrainException("Model not trained or loaded")
        query_vec = cls.model.transform([movie_title])
        similarity = cosine_similarity(query_vec, cls.matrix).flatten()
        indices = np.argsort(similarity)[-top_n:][::-1]
        return [cls.id_map[i] for i in indices]
