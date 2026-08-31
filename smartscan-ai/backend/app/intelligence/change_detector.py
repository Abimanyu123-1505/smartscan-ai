"""
smartscan.backend.app.intelligence.change_detector
===================================================
ChangeDetector: Monitors prediction error EMA & inter-arrival statistics
to trigger "Behavior shift detected — exploration increased" alerts.
"""

import numpy as np
from typing import Dict, List, Any, Optional


class ChangeDetector:
    """Detects regime shifts in RF emitter patterns."""

    def __init__(self, window_size: int = 20, threshold: float = 0.38):
        self.window_size = window_size
        self.threshold = threshold
        self.error_history: List[float] = []
        self.is_regime_shift = False

    def update(self, prediction_error: float) -> Dict[str, Any]:
        self.error_history.append(float(prediction_error))
        if len(self.error_history) > self.window_size:
            self.error_history.pop(0)

        mean_error = float(np.mean(self.error_history)) if self.error_history else 0.0
        
        # Trigger shift if recent error exceeds threshold
        if mean_error > self.threshold and not self.is_regime_shift:
            self.is_regime_shift = True
            msg = "Behavior shift detected — exploration increased."
        elif mean_error <= (self.threshold - 0.12) and self.is_regime_shift:
            self.is_regime_shift = False
            msg = "Behavior pattern stabilized."
        else:
            msg = "Normal regime"

        return {
            "is_regime_shift": self.is_regime_shift,
            "mean_error_ema": round(mean_error, 4),
            "message": msg,
            "exploration_boost_required": self.is_regime_shift
        }
