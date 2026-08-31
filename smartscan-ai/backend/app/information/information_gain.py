import numpy as np
from .entropy import shannon_entropy

class InformationGainEngine:
    @staticmethod
    def calculate_ig(prior_probs, expected_posterior_probs):
        h_prior = shannon_entropy(prior_probs)
        expected_h_posterior = np.mean([shannon_entropy(p) for p in expected_posterior_probs])
        return h_prior - expected_h_posterior
