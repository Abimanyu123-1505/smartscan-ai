"""
smartscan.backend.app.intelligence.uncertainty_engine
=====================================================
UncertaintyEngine: Calculates Predictive Entropy, Beta Variance, and Ensemble Variance.
Categorizes uncertainty into Epistemic vs Aleatoric components to guide adaptive exploration.
"""

import math
import numpy as np
from typing import Dict, List, Any, Tuple, Optional


class UncertaintyEngine:
    """Calculates uncertainty metrics over frequency channels to guide exploration."""

    @staticmethod
    def compute_predictive_entropy(probability: float) -> float:
        p = float(np.clip(probability, 1e-6, 1.0 - 1e-6))
        return float(-p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p))

    @staticmethod
    def compute_beta_variance(alpha: float, beta: float) -> float:
        total = alpha + beta
        if total <= 0:
            return 0.25
        var = (alpha * beta) / ((total ** 2) * (total + 1.0))
        # Scaled to [0, 1] range (max variance of Beta(1,1) is 1/12 ~ 0.0833)
        return float(np.clip(var * 12.0, 0.0, 1.0))

    @staticmethod
    def compute_ensemble_variance(predictions: List[float]) -> float:
        if len(predictions) < 2:
            return 0.0
        arr = np.asarray(predictions, dtype=float)
        return float(np.var(arr))

    @classmethod
    def evaluate_channel_uncertainty(cls, probability: float, alpha: float, beta: float, ensemble_probs: Optional[List[float]] = None) -> Dict[str, Any]:
        ent = cls.compute_predictive_entropy(probability)
        beta_var = cls.compute_beta_variance(alpha, beta)
        ens_var = cls.compute_ensemble_variance(ensemble_probs) if ensemble_probs else 0.0

        # Total Uncertainty Score (Weighted blend)
        total_score = float(np.clip(0.4 * ent + 0.4 * beta_var + 0.2 * (ens_var * 4.0), 0.0, 1.0))

        return {
            "predictive_entropy": round(ent, 4),
            "beta_variance": round(beta_var, 4),
            "ensemble_variance": round(ens_var, 4),
            "total_uncertainty_score": round(total_score, 4),
            "guidance": "HIGH_EXPLORATION" if total_score > 0.45 else "EXPLOITATION"
        }
