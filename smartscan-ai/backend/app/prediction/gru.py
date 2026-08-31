from .base import BasePredictor
import numpy as np

class GRUPredictor(BasePredictor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def fit(self, X, y):
        pass

    def predict(self, X):
        return np.zeros(len(X))

    def predict_proba(self, X):
        return np.zeros((len(X), 2))

    def save(self, path):
        pass

    def load(self, path):
        pass
