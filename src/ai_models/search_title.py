from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .base import ModelBase, TrainException

class SearchTitleModel(ModelBase, model_cache_path="search_title_cache.pkl"):
    model = None
    id_map = None
    matrix = None
    
    @classmethod
    async def load(cls, movie_titles: list[str] | None = None):
        if cache := await cls.load_cache():
            cls.model = cache["model"]
            cls.matrix = cache["matrix"]
            cls.id_map = cache["id_map"]
            return
        if movie_titles is None:
            raise TrainException("No cached model and no training data provided")
        await cls.train(movie_titles)

    @classmethod
    async def train(cls, movie_ids_titles: list[tuple[str, str]]):
        cls.id_map = {arr_id: id_title[0] for arr_id, id_title in enumerate(movie_ids_titles)}
        movie_titles = [id_title[1] for id_title in movie_ids_titles]
        cls.model = TfidfVectorizer(stop_words='english').fit(movie_titles)
        cls.matrix = cls.model.transform(movie_titles)
        cls.dump_cache({
            "matrix": cls.matrix,
            "model": cls.model,
            "id_map": cls.id_map
        })

    @classmethod
    async def predict(cls, movie_title: str, top_n: int = 20) -> list[str]:
        if not (cls.id_map and cls.model and cls.matrix):
            raise TrainException("Model not trained or loaded")
        query_vec = cls.model.transform([movie_title])
        similarity = cosine_similarity(query_vec, cls.model).flatten()
        indices = np.argpartition(similarity, -top_n)[-top_n:][::-1]
        return [cls.id_map[i] for i in indices]
