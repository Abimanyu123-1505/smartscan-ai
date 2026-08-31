"""
smartscan.backend.app.intelligence.periodicity_detector
======================================================
PeriodicityDetector: Discovers emission periods P, phase offsets,
and frequency transition probability matrices P(f_{t+1} | f_t).
"""

import numpy as np
from typing import Dict, List, Any, Optional


class PeriodicityDetector:
    """Discovers recurring pulse repetition intervals (PRI) and frequency movement patterns."""

    def __init__(self, num_freq_bins: int = 8):
        self.num_freq_bins = num_freq_bins
        # Frequency transition count matrix [from_bin, to_bin]
        self.transition_counts = np.zeros((num_freq_bins, num_freq_bins), dtype=float)

    def update_transition(self, prev_bin: int, curr_bin: int):
        if 0 <= prev_bin < self.num_freq_bins and 0 <= curr_bin < self.num_freq_bins:
            self.transition_counts[prev_bin, curr_bin] += 1.0

    def get_transition_matrix(self) -> np.ndarray:
        row_sums = self.transition_counts.sum(axis=1, keepdims=True)
        # Avoid division by zero
        row_sums[row_sums == 0] = 1.0
        return self.transition_counts / row_sums

    @staticmethod
    def detect_period(detection_history: List[int], current_slot: int) -> Dict[str, Any]:
        """Detects pulse repetition interval using autocorrelation over detection timestamps."""
        if len(detection_history) < 4:
            return {"detected": False, "confidence": 0.0, "reason": "NO RELIABLE PERIOD DETECTED"}

        arr = np.asarray(detection_history, dtype=float)
        indices = np.where(arr == 1)[0]

        if len(indices) < 3:
            return {"detected": False, "confidence": 0.0, "reason": "NO RELIABLE PERIOD DETECTED"}

        intervals = np.diff(indices)
        mean_period = float(np.mean(intervals))
        std_period = float(np.std(intervals))

        if mean_period <= 0:
            return {"detected": False, "confidence": 0.0, "reason": "NO RELIABLE PERIOD DETECTED"}

        confidence = float(np.clip(1.0 - (std_period / mean_period), 0.0, 1.0))
        detected = confidence >= 0.50 and len(intervals) >= 2

        if not detected:
            return {"detected": False, "confidence": round(confidence, 4), "reason": "NO RELIABLE PERIOD DETECTED"}

        last_hit = indices[-1]
        period = int(round(mean_period))
        next_event = last_hit + period
        while next_event <= current_slot:
            next_event += period

        return {
            "detected": True,
            "period_slots": period,
            "confidence": round(confidence, 4),
            "next_event_slot": next_event,
            "slots_until_next": next_event - current_slot
        }
