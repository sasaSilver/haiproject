from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
from .base import ModelBase, TrainException
from src.database.models import RatingSchema

class CollaborativeFilteringModel(ModelBase, model_cache_path="collab_filtering_cache.pkl"):
    model = None
    user_map = None
    item_map = None
    user_items = None
    
    @classmethod
    def load(cls, ratings: list[RatingSchema] | None = None):
        if cache := cls.load_cache():
            cls.model = cache["model"]
            cls.user_map = cache["user_map"]
            cls.item_map = cache["item_map"]
            cls.user_items = cache["user_items"]
            return
        if ratings is None:
            raise TrainException("No cached model and no training data provided")
        cls.train(ratings)

    @classmethod
    def train(cls, ratings: list[RatingSchema]):
        unique_users = {r.user_id for r in ratings}
        unique_items = {r.movie_id for r in ratings}
        
        cls.user_map = {user_id: idx for idx, user_id in enumerate(unique_users)}
        cls.item_map = {item_id: idx for idx, item_id in enumerate(unique_items)}
        
        user_indices = [cls.user_map[r.user_id] for r in ratings]
        item_indices = [cls.item_map[r.movie_id] for r in ratings]
        
        values = [1 for _ in ratings]
        
        cls.user_items = coo_matrix(
            (values, (user_indices, item_indices)),
            shape=(len(cls.user_map), len(cls.item_map))
        ).tocsr()
        
        cls.model = AlternatingLeastSquares(
            factors=64,
            regularization=0.01,
            iterations=15
        )
        
        cls.model.fit(cls.user_items)
        
        cls.dump_cache({
            "model": cls.model,
            "user_map": cls.user_map,
            "item_map": cls.item_map,
            "user_items": cls.user_items
        })

    @classmethod
    def predict(cls, user_id: int, top_n: int = 10) -> list[str]:
        if not (cls.user_map and cls.item_map and cls.model and cls.user_items):
            raise TrainException("Model not trained or loaded")
            
        if user_id not in cls.user_map:
            return []
            
        user_idx = cls.user_map[user_id]
        
        items, scores = cls.model.recommend(
            user_idx,
            cls.user_items[user_idx],
            N=top_n,
            filter_already_liked_items=True
        )
        
        reverse_item_map = {v: k for k, v in cls.item_map.items()}
        return [reverse_item_map[i] for i in items if i in reverse_item_map]