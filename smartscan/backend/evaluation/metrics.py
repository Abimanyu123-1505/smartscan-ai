"""
metrics.py
==========
Evaluation metrics for the SmartScan replay experiments.
All metrics are computed against REAL recording events.

Primary metrics (operationally meaningful):
  1. Interception Rate = fraction of events detected by receiver
  2. Mean/Median/P95 Intercept Time (slots from event start to first detection)
  3. Pd = P(detect | event present in observed window)
  4. Pfa = P(detect | no event in observed window)
  5. Spectrum Coverage = fraction of freq bins visited

Secondary metrics:
  - Prediction accuracy (when predictor is active)
  - Average reward
  - Switching count
"""

import numpy as np
from typing import List, Dict, Any, Optional
from ..preprocessing.event_detector import RFEvent
from ..replay.replay_receiver import ReceiverObservation

class EvaluationSession:
    def __init__(self, recording_id: str, policy_name: str, events: List[RFEvent]):
        self.recording_id = recording_id
        self.policy_name = policy_name
        self.events = events
        
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0
        self.total_observations = 0
        self._switch_count = 0
        self._visited_bins = set()
        
        # Track detection time per event
        self._event_intercept_slots: Dict[str, int] = {}
        # Track if event was EVER detected
        self._event_caught: Dict[str, bool] = {e.event_id: False for e in events}
        # Helper map
        self._event_start: Dict[str, int] = {e.event_id: e.start_slot for e in events}

    def record_observation(self, obs: ReceiverObservation, truth_active: bool, event_id: Optional[str]):
        self.total_observations += 1
        self._visited_bins.add(obs.frequency_bin)
        
        if obs.switched:
            self._switch_count += 1
            
        if truth_active:
            if obs.detected:
                self.tp += 1
                if event_id:
                    self._event_caught[event_id] = True
                    if event_id not in self._event_intercept_slots:
                        delay = obs.time_slot - self._event_start[event_id]
                        self._event_intercept_slots[event_id] = max(0, delay)
            else:
                self.fn += 1
        else:
            if obs.detected:
                self.fp += 1
            else:
                self.tn += 1

    def pd(self) -> float:
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    def pfa(self) -> float:
        if (self.fp + self.tn) == 0:
            return 0.0
        return self.fp / (self.fp + self.tn)

    def f1(self) -> float:
        prec = self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0
        rec = self.pd()
        if (prec + rec) == 0:
            return 0.0
        return 2 * (prec * rec) / (prec + rec)

    def interception_rate(self) -> float:
        if not self.events:
            return 1.0
        caught = sum(1 for v in self._event_caught.values() if v)
        return caught / len(self.events)

    def _intercept_times(self) -> List[int]:
        return list(self._event_intercept_slots.values())

    def mean_intercept_time(self) -> float:
        times = self._intercept_times()
        return float(np.mean(times)) if times else 0.0

    def median_intercept_time(self) -> float:
        times = self._intercept_times()
        return float(np.median(times)) if times else 0.0

    def p95_intercept_time(self) -> float:
        times = self._intercept_times()
        return float(np.percentile(times, 95)) if times else 0.0

    def spectrum_coverage(self, n_freq: int) -> float:
        if n_freq == 0:
            return 0.0
        return len(self._visited_bins) / n_freq

    def switching_count(self) -> int:
        return self._switch_count

    def summary(self) -> Dict[str, Any]:
        return {
            "recording_id": self.recording_id,
            "policy_name": self.policy_name,
            "interception_rate": self.interception_rate(),
            "mean_intercept_time_slots": self.mean_intercept_time(),
            "median_intercept_time_slots": self.median_intercept_time(),
            "p95_intercept_time_slots": self.p95_intercept_time(),
            "pd": self.pd(),
            "pfa": self.pfa(),
            "f1": self.f1(),
            "switching_count": self.switching_count(),
            "total_observations": self.total_observations,
            "events_total": len(self.events),
            "events_caught": sum(1 for v in self._event_caught.values() if v)
        }

class MultiPolicyEvaluator:
    def __init__(self):
        self.results = {}

    def run_all(self, engine_factory, policies: List[Any], n_ticks: int) -> Dict[str, Dict[str, Any]]:
        for policy in policies:
            # Recreate engine to ensure exact same conditions
            engine, receiver, belief, events = engine_factory()
            evaluator = EvaluationSession(engine.recording_meta.recording_id, policy.name, events)
            
            from ..policies.base import PolicyContext
            
            for _ in range(n_ticks):
                if engine.is_finished():
                    break
                    
                context = PolicyContext(
                    current_slot=engine.current_slot,
                    current_freq_bin=receiver.current_frequency_bin,
                    num_freq_bins=engine.num_freq_bins,
                    belief_state=belief,
                    last_observation=None, # simplification
                    config={}
                )
                
                next_freq = policy.select(context)
                obs = receiver.select_frequency(next_freq)
                truth = engine.get_evaluation_truth(engine.current_slot, next_freq)
                
                evaluator.record_observation(obs, truth['active'], truth['event_id'])
                
                engine.advance()
                
            self.results[policy.name] = evaluator.summary()
            
        return self.results

    def comparison_table(self) -> List[Dict[str, Any]]:
        return list(self.results.values())
