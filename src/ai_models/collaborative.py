from scipy.sparse import coo_matrix, csr_matrix
from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import bm25_weight
from src.database.models import RatingSchema
from .utils import TrainException
from .base import ModelBase

class CollaborativeFilteringModel(ModelBase, model_cache_path="collab_filtering_cache.pkl"):
    model = None
    user_map = None
    item_map = None
    user_items = None
    reverse_item_map = None
    
    @classmethod
    def load(cls):
        if cache := cls.load_cache():
            cls.model = cache["model"]
            cls.user_map = cache["user_map"]
            cls.item_map = cache["item_map"]
            cls.user_items = cache["user_items"]
            cls.reverse_item_map = cache["reverse_item_map"]
            if None in [cls.model, cls.user_map, cls.item_map, cls.user_items, cls.reverse_item_map]:
                raise TrainException("Incomplete cache data")
            return
        raise TrainException(f"{cls.__name__} missing cache.")

    @classmethod
    def train(cls, ratings: list[RatingSchema]):
        if not ratings:
            raise TrainException("No ratings provided for training")

        unique_users = {r.user_id for r in ratings}
        unique_items = {r.movie_id for r in ratings}
        
        cls.user_map = {user_id: idx for idx, user_id in enumerate(unique_users)}
        cls.item_map = {item_id: idx for idx, item_id in enumerate(unique_items)}
        cls.reverse_item_map = {v: k for k, v in cls.item_map.items()}
        
        user_indices = [cls.user_map[r.user_id] for r in ratings]
        item_indices = [cls.item_map[r.movie_id] for r in ratings]
        
        values = [r.rating if hasattr(r, 'rating') else 1 for r in ratings]
        
        cls.user_items = coo_matrix(
            (values, (user_indices, item_indices)),
            shape=(len(cls.user_map), len(cls.item_map))
        ).tocsr()
        
        cls.user_items = bm25_weight(cls.user_items, K1=100, B=0.8)
        
        cls.model = AlternatingLeastSquares(
            factors=128,
            regularization=0.01,
            iterations=50,
            random_state=42
        )
        
        cls.model.fit(2 * cls.user_items)
        
        cls.dump_cache({
            "model": cls.model,
            "user_map": cls.user_map,
            "item_map": cls.item_map,
            "user_items": cls.user_items,
            "reverse_item_map": cls.reverse_item_map
        })

    @classmethod
    def predict(cls, user_id: int, top_n: int = 10) -> list[str]:
        if cls.user_map is None or cls.user_items is None or cls.item_map is None:
            raise TrainException("Model not trained or loaded")
            
        if user_id not in cls.user_map:
            return []
            
        user_idx = cls.user_map[user_id]
        user_items_csr = cls.user_items[user_idx].reshape(1, -1) if isinstance(cls.user_items, csr_matrix) else \
                        csr_matrix((1, cls.user_items.shape[1]), dtype=cls.user_items.dtype)
        
        items, scores = cls.model.recommend(
            userid=user_idx,
            user_items=user_items_csr,
            N=top_n,
            filter_already_liked_items=True,
            recalculate_user=True
        )
        
        return [cls.reverse_item_map[i] for i in items if i in cls.reverse_item_map]

    @classmethod
    def similar_items(cls, item_id: int, top_n: int = 10) -> list[str]:
        if cls.item_map is None or cls.model is None:
            raise TrainException("Model not trained or loaded")
            
        if item_id not in cls.item_map:
            return []
            
        item_idx = cls.item_map[item_id]
        items = cls.model.similar_items(item_idx, N=top_n)
        
        return [cls.reverse_item_map[i] for i in items if i in cls.reverse_item_map]
    
    @classmethod
    def dump(cls):
        cls.dump_cache({
            "model": cls.model,
            "user_map": cls.user_map,
            "item_map": cls.item_map,
            "user_items": cls.user_items,
            "reverse_item_map": cls.reverse_item_map
        })