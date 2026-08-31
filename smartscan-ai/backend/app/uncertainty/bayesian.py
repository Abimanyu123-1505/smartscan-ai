import numpy as np
from .base import BaseUncertaintyEngine

class BayesianUncertaintyEngine(BaseUncertaintyEngine):
    def __init__(self, alpha=1.0, beta=1.0):
        self.alpha = alpha
        self.beta = beta

    def calculate_uncertainty(self, pos_counts, total_counts):
        a = self.alpha + pos_counts
        b = self.beta + total_counts - pos_counts
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
