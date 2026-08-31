from .base import BasePredictor
import numpy as np

class EnsemblePredictor(BasePredictor):
    def __init__(self, predictors, weights=None, **kwargs):
        super().__init__(**kwargs)
        self.predictors = predictors
        self.weights = weights if weights is not None else [1.0/len(predictors)] * len(predictors)

    def fit(self, X, y):
        for p in self.predictors:
            p.fit(X, y)

    def predict(self, X):
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

    def predict_proba(self, X):
        res = 0
        for w, p in zip(self.weights, self.predictors):
            res += w * p.predict_proba(X)
        return res

    def save(self, path):
        pass

    def load(self, path):
        pass
