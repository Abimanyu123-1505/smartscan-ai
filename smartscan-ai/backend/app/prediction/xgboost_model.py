from .base import BasePredictor
import numpy as np

class XGBoostPredictor(BasePredictor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = None # Fallback or actual xgboost
    
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
