import time
from typing import Dict, Any, Tuple


class LatencyProfiler:
    """Measures pipeline timing breakdown per tick."""

    def __init__(self):
        self.dsp_latency_ms = 0.0
        self.prediction_latency_ms = 0.0
        self.policy_latency_ms = 0.0
        self.total_latency_ms = 0.0

    def profile_step(self, dsp_fn, pred_fn, policy_fn) -> Tuple[Any, Dict[str, float]]:
        t0 = time.perf_counter()
        dsp_res = dsp_fn()
        t1 = time.perf_counter()
        
        pred_res = pred_fn(dsp_res)
        t2 = time.perf_counter()

        policy_res = policy_fn(pred_res)
        t3 = time.perf_counter()

        self.dsp_latency_ms = (t1 - t0) * 1000.0
        self.prediction_latency_ms = (t2 - t1) * 1000.0
        self.policy_latency_ms = (t3 - t2) * 1000.0
        self.total_latency_ms = (t3 - t0) * 1000.0

        return policy_res, self.to_dict()

    def to_dict(self) -> Dict[str, float]:
        return {
            "dsp_latency_ms": round(self.dsp_latency_ms, 3),
            "prediction_latency_ms": round(self.prediction_latency_ms, 3),
            "policy_latency_ms": round(self.policy_latency_ms, 3),
            "total_latency_ms": round(self.total_latency_ms, 3),
        }
