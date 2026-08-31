from .base import BasePredictor
import numpy as np

class MarkovPredictor(BasePredictor):
    def __init__(self, order=1, **kwargs):
        super().__init__(**kwargs)
        self.order = order
        self.transition_matrix = {}
        self.classes = None
        self.last_state = None

    def fit(self, X, y):
        self.classes = np.unique(y)
        for i in range(len(y) - 1):
            curr = y[i]
            nxt = y[i+1]
            if curr not in self.transition_matrix:
                self.transition_matrix[curr] = {}
            if nxt not in self.transition_matrix[curr]:
                self.transition_matrix[curr][nxt] = 0
            self.transition_matrix[curr][nxt] += 1
        
        for curr in self.transition_matrix:
            total = sum(self.transition_matrix[curr].values())
            for nxt in self.transition_matrix[curr]:
                self.transition_matrix[curr][nxt] /= total
        if len(y) > 0:
            self.last_state = y[-1]

    def predict(self, X):
        return np.array([self._predict_single() for _ in range(len(X))])

    def _predict_single(self):
        if self.last_state not in self.transition_matrix:
            return self.classes[0] if self.classes is not None else 0
        probs = self.transition_matrix[self.last_state]
        return max(probs, key=probs.get)

    def predict_proba(self, X):
        num_classes = len(self.classes) if self.classes is not None else 2
        res = np.zeros((len(X), num_classes))
        for i in range(len(X)):
            if self.last_state in self.transition_matrix:
                for j, c in enumerate(self.classes):
                    res[i, j] = self.transition_matrix[self.last_state].get(c, 0.0)
        return res

    def save(self, path):
        pass

    def load(self, path):
        pass
