"""
smartscan.backend.app.intelligence.information_gain
===================================================
InformationGainEngine: Calculates expected information gain IG(a) = H(b_t) - E[H(b_{t+1}) | a].
Supports Value-of-Information (VOI) trade-offs between immediate detection and uncertainty reduction.
"""

import math
import numpy as np
from typing import Dict, Any


class InformationGainEngine:
    """Computes entropy reduction expected from observing candidate frequency channels."""

    @staticmethod
    def entropy(p: float) -> float:
        p_c = float(np.clip(p, 1e-6, 1.0 - 1e-6))
        return float(-p_c * math.log2(p_c) - (1.0 - p_c) * math.log2(1.0 - p_c))

    @classmethod
    def compute_information_gain(cls, current_p: float, obs_count: int) -> float:
        """
        Computes expected information gain IG(a) = H(b_t) - E[H(b_{t+1}) | a].
        Channels with high current entropy H(b_t) and low observation count yield higher IG.
        """
        h_current = cls.entropy(current_p)
        
        # Expected posterior entropy assuming observation arrives
        p_detect = current_p
        h_if_detected = cls.entropy(0.90)  # High posterior confidence
        h_if_missed = cls.entropy(0.10)

        h_expected_next = p_detect * h_if_detected + (1.0 - p_detect) * h_if_missed
        
        # Recency / observation count attenuation factor
        attenuation = 1.0 / (1.0 + obs_count * 0.25)
        raw_ig = max(0.0, h_current - h_expected_next)
        
        ig_score = float(np.clip(raw_ig * attenuation + h_current * 0.2 * attenuation, 0.0, 1.0))
        return round(ig_score, 4)
