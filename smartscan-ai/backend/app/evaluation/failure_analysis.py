"""
smartscan.backend.app.evaluation.failure_analysis
=================================================
Failure Case Analysis & Replay Snippet Extraction.
Logs prediction errors, missed events, false alarms, and frequency starvation gaps.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class FailureEvent:
    failure_id: str
    event_type: str               # "FALSE_ALARM", "MISSED_INTERCEPT", "HIGH_PRED_ERROR", "STARVATION"
    timestamp_slot: int
    frequency_bin: int
    predicted_probability: float
    actual_state: int
    description: str
    revisit_gap_slots: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "event_type": self.event_type,
            "timestamp_slot": self.timestamp_slot,
            "frequency_bin": self.frequency_bin,
            "predicted_probability": round(float(self.predicted_probability), 4),
            "actual_state": self.actual_state,
            "description": self.description,
            "revisit_gap_slots": self.revisit_gap_slots,
        }


class FailureCaseLogger:
    """Logs and categorizes failure cases during evaluation runs."""

    def __init__(self):
        self.failures: List[FailureEvent] = []

    def log_failure(
        self,
        event_type: str,
        slot: int,
        freq_bin: int,
        pred_prob: float,
        actual: int,
        description: str,
        gap: Optional[int] = None
    ) -> FailureEvent:
        failure_id = f"fail_{len(self.failures) + 1:04d}"
        ev = FailureEvent(
            failure_id=failure_id,
            event_type=event_type,
            timestamp_slot=slot,
            frequency_bin=freq_bin,
            predicted_probability=pred_prob,
            actual_state=actual,
            description=description,
            revisit_gap_slots=gap
        )
        self.failures.append(ev)
        return ev

    def get_summary(self) -> Dict[str, Any]:
        counts = {}
        for f in self.failures:
            counts[f.event_type] = counts.get(f.event_type, 0) + 1
        return {
            "total_failures": len(self.failures),
            "by_type": counts,
            "recent_failures": [f.to_dict() for f in self.failures[-20:]],
        }
