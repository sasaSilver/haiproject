import pickle
import os

class ModelBase:
    def __init_subclass__(cls, model_cache_path: str, **kwargs):
        super().__init_subclass__()
        cls.model_cache_path = 'src/ai_models/trained/' + model_cache_path
    
    @classmethod
    async def load_cache(cls):
        if os.path.exists(cls.model_cache_path):
            return None
        with open(cls.model_cache_path, "rb") as f:
            return pickle.load(f)

    @classmethod
    async def dump_cache(cls, cache):
        with open(cls.model_cache_path, "wb") as f:
            pickle.dump(cache, f)

class TrainException(Exception):
    def __init__(self, *args):
        super().__init__(*args)