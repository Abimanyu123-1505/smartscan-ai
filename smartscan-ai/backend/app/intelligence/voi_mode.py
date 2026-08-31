"""
smartscan.backend.app.intelligence.voi_mode
===========================================
Value-of-Information (VOI) Mode: Breaks down candidate sensing actions into:
- Immediate Detection Value
- Information Gain
- Future Utility
- Switch Cost
- Total VOI Utility
"""

from typing import Dict, List, Any, Optional


class VOIEngine:
    """Calculates Value of Information (VOI) breakdown per candidate action."""

    @staticmethod
    def calculate_voi(
        freq_bin: int,
        predicted_prob: float,
        info_gain: float,
        uncertainty: float,
        periodicity_score: float,
        is_switched: bool,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        W = weights or {
            "immediate": 0.35,
            "info_gain": 0.25,
            "future": 0.20,
            "switch_cost": 0.10,
            "delay_cost": 0.10
        }

        immediate_val = predicted_prob
        ig_val = info_gain
        future_val = periodicity_score * 0.7 + uncertainty * 0.3
        switch_cost = 1.0 if is_switched else 0.0
        delay_cost = 0.5 if is_switched else 0.0

        total_voi = (
            W["immediate"] * immediate_val +
            W["info_gain"] * ig_val +
            W["future"] * future_val -
            W["switch_cost"] * switch_cost -
            W["delay_cost"] * delay_cost
        )

        explanation = (
            f"F{freq_bin+1} selected: High information gain ({ig_val:.2f}) and immediate detection value ({immediate_val:.2f})."
            if ig_val > 0.4 else
            f"F{freq_bin+1} selected based on high predicted activity ({immediate_val:.2f})."
        )

        return {
            "frequency_bin": freq_bin,
            "immediate_detection_value": round(float(immediate_val), 4),
            "information_gain": round(float(ig_val), 4),
            "future_utility": round(float(future_val), 4),
            "switch_cost": round(float(switch_cost), 4),
            "total_voi_utility": round(float(total_voi), 4),
            "natural_explanation": explanation
        }
