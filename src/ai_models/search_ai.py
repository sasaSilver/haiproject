from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .base import ModelBase
from .utils import TrainException

class SearchAiModel(ModelBase, model_cache_path="search_keywords_cache.pkl"):
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
    def train(cls, movie_ids_keywords: list[tuple[str, list[str]]]):
        cls.id_map = {arr_id: movie_id for arr_id, (movie_id, _) in enumerate(movie_ids_keywords)}
        keyword_lists = [' '.join(keywords) for _, keywords in movie_ids_keywords]
        
        cls.model = TfidfVectorizer(
            strip_accents="ascii",
            ngram_range=(1, 2)
        ).fit(keyword_lists)
        cls.matrix = cls.model.transform(keyword_lists)
        cls.dump_cache({
            "matrix": cls.matrix,
            "model": cls.model,
            "id_map": cls.id_map
        })

    @classmethod
    def predict(cls, query_keywords: list[str], top_n: int = 20) -> list[str]:
        if any([cls.id_map is None and cls.model is None and cls.matrix is None]):
            raise TrainException("Model not trained or loaded")
            
        query_vec = cls.model.transform([query_keywords])
        similarity = cosine_similarity(query_vec, cls.matrix).flatten()
        indices = np.argsort(similarity)[-top_n:][::-1]
        return [cls.id_map[i] for i in indices if similarity[i] > 0][::-1]
    
    @classmethod
    def dump(cls):
        cls.dump_cache({
            "matrix": cls.matrix,
            "model": cls.model,
            "id_map": cls.id_map
        })