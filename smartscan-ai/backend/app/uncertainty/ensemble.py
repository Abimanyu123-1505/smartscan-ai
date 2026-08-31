import numpy as np
from .base import BaseUncertaintyEngine

class EnsembleUncertaintyEngine(BaseUncertaintyEngine):
    def calculate_uncertainty(self, probs_list):
        # probs_list shape: (n_models, n_samples, n_classes)
        probs_array = np.array(probs_list)
        return np.var(probs_array, axis=0).mean(axis=-1)
