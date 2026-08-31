"""
smartscan.backend.app.evaluation.counterfactual
================================================
Counterfactual Decision Replay Engine.
Reconstructs exact observations, predictions, uncertainty, periodicity,
and utility scores available at time t = X, then reveals what actually occurred afterward.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class DecisionSnapshot:
    time_slot: int
    selected_frequency_bin: int
    selected_frequency_label: str
    observations_available: Dict[str, Any]
    model_predictions: List[float]
    uncertainty_scores: List[float]
    periodicity_scores: List[float]
    info_gain_scores: List[float]
    candidate_utility_scores: List[float]
    natural_language_explanation: str
    actual_ground_truth_state: int
    actual_detection_outcome: bool
    revisit_gap_afterward: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_slot": self.time_slot,
            "selected_frequency_bin": self.selected_frequency_bin,
            "selected_frequency_label": self.selected_frequency_label,
            "observations_available": self.observations_available,
            "model_predictions": [round(float(p), 4) for p in self.model_predictions],
            "uncertainty_scores": [round(float(u), 4) for u in self.uncertainty_scores],
            "periodicity_scores": [round(float(ps), 4) for ps in self.periodicity_scores],
            "info_gain_scores": [round(float(ig), 4) for ig in self.info_gain_scores],
            "candidate_utility_scores": [round(float(ut), 4) for ut in self.candidate_utility_scores],
            "natural_language_explanation": self.natural_language_explanation,
            "actual_ground_truth_state": self.actual_ground_truth_state,
            "actual_detection_outcome": self.actual_detection_outcome,
            "revisit_gap_afterward": self.revisit_gap_afterward,
        }


class CounterfactualReplayEngine:
    """Stores and retrieves historical decision snapshots for counterfactual inspection."""

    def __init__(self):
        self.snapshots: Dict[int, DecisionSnapshot] = {}

    def log_snapshot(self, snapshot: DecisionSnapshot):
        self.snapshots[snapshot.time_slot] = snapshot

    def get_snapshot(self, time_slot: int) -> Optional[Dict[str, Any]]:
        snap = self.snapshots.get(time_slot)
        return snap.to_dict() if snap else None
