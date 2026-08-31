from .base import BasePredictor
import numpy as np

class PersistencePredictor(BasePredictor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_value = None
        self.classes = None

    def fit(self, X, y):
        self.classes = np.unique(y)
        if len(y) > 0:
            self.last_value = y[-1]

    def predict(self, X):
        if self.last_value is None:
            return np.zeros(len(X))
        return np.full(len(X), self.last_value)

    def predict_proba(self, X):
        proba = np.zeros((len(X), len(self.classes) if self.classes is not None else 2))
        if self.last_value is not None and self.classes is not None:
            idx = np.where(self.classes == self.last_value)[0][0]
            proba[:, idx] = 1.0
        return proba

    def save(self, path):
        pass

    def load(self, path):
        pass
