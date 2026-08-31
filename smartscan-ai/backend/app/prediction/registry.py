class PredictorRegistry:
    _registry = {}

    @classmethod
    def register(cls, name, predictor_cls):
        cls._registry[name] = predictor_cls

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

    @classmethod
    def list(cls):
        return list(cls._registry.keys())

# Register defaults
from .persistence import PersistencePredictor
from .markov import MarkovPredictor
from .random_forest import RandomForestPredictor
from .xgboost_model import XGBoostPredictor
from .gru import GRUPredictor
from .transformer import TransformerPredictor
from .ensemble import EnsemblePredictor

PredictorRegistry.register("persistence", PersistencePredictor)
PredictorRegistry.register("markov", MarkovPredictor)
PredictorRegistry.register("random_forest", RandomForestPredictor)
PredictorRegistry.register("xgboost", XGBoostPredictor)
PredictorRegistry.register("gru", GRUPredictor)
PredictorRegistry.register("transformer", TransformerPredictor)
PredictorRegistry.register("ensemble", EnsemblePredictor)
