"""
smartscan.backend.app.intelligence.multi_emitter
================================================
Multi-Emitter Resource Allocation & Coverage Evaluator.
Evaluates event coverage, fairness, priority, and miss rate across multiple targets.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class EmitterTarget:
    target_id: str
    freq_bin: int
    priority: float  # 1.0 (High) to 0.1 (Low)
    label: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "freq_bin": self.freq_bin,
            "priority": self.priority,
            "label": self.label
        }


class MultiEmitterAllocator:
    """Allocates narrowband receiver sensing slots across multiple simultaneous targets."""

    def __init__(self, targets: List[EmitterTarget]):
        self.targets = targets
        self.visit_counts = {t.target_id: 0 for t in targets}
        self.intercept_counts = {t.target_id: 0 for t in targets}

    def record_visit(self, freq_bin: int, intercepted: bool = False):
        for t in self.targets:
            if t.freq_bin == freq_bin:
                self.visit_counts[t.target_id] += 1
                if intercepted:
                    self.intercept_counts[t.target_id] += 1

    def compute_fairness_and_coverage(self) -> Dict[str, Any]:
        counts = list(self.visit_counts.values())
        total_visits = sum(counts)
        
        # Jain's Fairness Index
        if total_visits == 0 or len(counts) == 0:
            jain_index = 1.0
        else:
            jain_index = (sum(counts) ** 2) / (len(counts) * sum(c ** 2 for c in counts)) if sum(c ** 2 for c in counts) > 0 else 1.0

        target_stats = []
        for t in self.targets:
            v = self.visit_counts[t.target_id]
            ic = self.intercept_counts[t.target_id]
            target_stats.append({
                "target_id": t.target_id,
                "freq_bin": t.freq_bin,
                "label": t.label,
                "visits": v,
                "intercepts": ic,
                "visit_share": round(v / total_visits, 4) if total_visits > 0 else 0.0
            })

        return {
            "total_targets": len(self.targets),
            "total_visits": total_visits,
            "jains_fairness_index": round(float(jain_index), 4),
            "target_statistics": target_stats
        }
