from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .base import ModelBase, TrainException

class SearchKeywordsModel(ModelBase, model_cache="search_keywords_cache.pkl"):
    model = None
    id_map = None
    matrix = None
    
    @classmethod
    def load(cls, movie_ids_keywords: list[tuple[str, list[str]]] | None = None):
        if cache := cls.load_cache():
            cls.model = cache["model"]
            cls.matrix = cache["matrix"]
            cls.id_map = cache["id_map"]
            return
        if movie_ids_keywords is None:
            raise TrainException("No cached model and no training data provided")
        cls.train(movie_ids_keywords)

    @classmethod
    def train(cls, movie_ids_keywords: list[tuple[str, list[str]]]):
        cls.id_map = {arr_id: movie_id for arr_id, (movie_id, _) in enumerate(movie_ids_keywords)}
        keyword_lists = [keywords for _, keywords in movie_ids_keywords]
        
        cls.model = TfidfVectorizer(
            tokenizer=lambda x: x,
            preprocessor=lambda x: x,
            token_pattern=None,
            lowercase=True,
            analyzer='word'
        )
        
        cls.matrix = cls.model.fit_transform(keyword_lists)
        cls.dump_cache({
            "matrix": cls.matrix,
            "model": cls.model,
            "id_map": cls.id_map
        })

    @classmethod
    def predict(cls, query_keywords: list[str], top_n: int = 20) -> list[str]:
        if not (cls.id_map and cls.model and cls.matrix):
            raise TrainException("Model not trained or loaded")
            
        query_vec = cls.model.transform([query_keywords])
        similarity = cosine_similarity(query_vec, cls.matrix).flatten()
        indices = np.argpartition(similarity, -top_n)[-top_n:][::-1]
        return [cls.id_map[i] for i in indices if similarity[i] > 0]