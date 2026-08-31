"""
belief_state.py
===============
Maintains the scheduler's belief about the RF environment.
Built ONLY from receiver observations — no access to hidden data.

Per-frequency state:
  - activity_estimate    : rolling estimate of P(active)
  - uncertainty          : Beta-distribution variance
  - last_observed_slot   : recency
  - recent_detections    : sliding window detection sequence
  - ewma                 : exponential weighted moving average of detections
  - alpha, beta          : Beta distribution parameters (Bayesian)
  - periodicity          : autocorrelation-derived period estimate
  - observation_count    : total times this frequency was observed
  - detection_count      : total detections
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import numpy as np
from ..replay.replay_receiver import ReceiverObservation

@dataclass
class FrequencyBelief:
    freq_bin: int
    freq_hz: float
    alpha: float = 1.0  # Beta prior
    beta: float = 1.0
    ewma: float = 0.25
    last_observed_slot: int = -999
    observation_count: int = 0
    detection_count: int = 0
    detection_history: List[int] = field(default_factory=list)  # 0/1 per observation
    power_history: List[float] = field(default_factory=list)  # dB readings

    @property
    def activity_estimate(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def uncertainty(self) -> float:
        # Beta distribution variance
        return (self.alpha * self.beta) / ((self.alpha + self.beta) ** 2 * (self.alpha + self.beta + 1))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "freq_bin": self.freq_bin,
            "freq_hz": self.freq_hz,
            "activity_estimate": self.activity_estimate,
            "uncertainty": self.uncertainty,
            "last_observed_slot": self.last_observed_slot,
            "observation_count": self.observation_count,
            "detection_count": self.detection_count,
            "ewma": self.ewma
        }

class BeliefState:
    def __init__(self, freq_bins_hz: List[float]):
        self.beliefs = [FrequencyBelief(freq_bin=i, freq_hz=hz) for i, hz in enumerate(freq_bins_hz)]
        self._n_bins = len(freq_bins_hz)

    def update(self, freq_bin: int, time_slot: int, observation: ReceiverObservation):
        b = self.beliefs[freq_bin]
        b.last_observed_slot = time_slot
        b.observation_count += 1
        
        detected_val = 1 if observation.detected else 0
        b.detection_count += detected_val
        b.detection_history.append(detected_val)
        b.power_history.append(observation.power_db)
        
        # Update Beta dist
        if observation.detected:
            b.alpha += 1.0
        else:
            b.beta += 1.0
            
        # Update EWMA
        alpha_ewma = 0.1
        b.ewma = alpha_ewma * detected_val + (1 - alpha_ewma) * b.ewma

    def get_belief(self, freq_bin: int) -> FrequencyBelief:
        return self.beliefs[freq_bin]

    def all_beliefs(self) -> List[FrequencyBelief]:
        return self.beliefs

    def get_activity_estimates(self) -> np.ndarray:
        return np.array([b.activity_estimate for b in self.beliefs])

    def get_uncertainties(self) -> np.ndarray:
        return np.array([b.uncertainty for b in self.beliefs])

    def detect_periodicity(self, freq_bin: int) -> Dict[str, Any]:
        """Periodicity detection uses autocorrelation of detection_history"""
        b = self.beliefs[freq_bin]
        history = np.array(b.detection_history)
        if len(history) < 10 or np.sum(history) < 2:
            return {"detected": False, "period_slots": None, "phase": None, "confidence": 0.0, "next_event_slot": None}
            
        # Auto-correlation
        hist_mean = history - np.mean(history)
        autocorr = np.correlate(hist_mean, hist_mean, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        if np.var(history) == 0:
            return {"detected": False, "period_slots": None, "phase": None, "confidence": 0.0, "next_event_slot": None}
            
        autocorr /= np.var(history) * len(history)
        
        # Find peaks
        peaks = []
        for i in range(1, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                peaks.append((i, autocorr[i]))
                
        if not peaks:
            return {"detected": False, "period_slots": None, "phase": None, "confidence": 0.0, "next_event_slot": None}
            
        peaks.sort(key=lambda x: x[1], reverse=True)
        best_lag, best_corr = peaks[0]
        
        if best_corr > 0.3:
            return {
                "detected": True, 
                "period_slots": best_lag,
                "phase": None, # Complex to compute precisely without timestamps
                "confidence": float(best_corr),
                "next_event_slot": b.last_observed_slot + best_lag
            }
            
        return {"detected": False, "period_slots": None, "phase": None, "confidence": 0.0, "next_event_slot": None}

    def compute_information_gain(self, freq_bin: int) -> float:
        """entropy reduction estimate"""
        return self.beliefs[freq_bin].uncertainty

    def global_uncertainty(self) -> float:
        return float(np.mean(self.get_uncertainties()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "global_uncertainty": self.global_uncertainty(),
            "beliefs": [b.to_dict() for b in self.beliefs]
        }
