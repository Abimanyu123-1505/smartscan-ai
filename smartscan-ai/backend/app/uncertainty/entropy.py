import numpy as np
from .base import BaseUncertaintyEngine

class EntropyUncertaintyEngine(BaseUncertaintyEngine):
    def calculate_uncertainty(self, probs):
        probs = np.clip(probs, 1e-9, 1 - 1e-9)
        return -np.sum(probs * np.log(probs), axis=-1)
