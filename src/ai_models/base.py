import pickle
import os

class ModelBase:
    def __init_subclass__(cls, model_cache_path: str):
        super().__init_subclass__()
        cls.model_cache_path = 'src/ai_models/trained/' + model_cache_path
    
    @classmethod
    def load_cache(cls):
        try:
            with open(cls.model_cache_path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    @classmethod
    def dump_cache(cls, cache):
        with open(cls.model_cache_path, "wb") as f:
            pickle.dump(cache, f)