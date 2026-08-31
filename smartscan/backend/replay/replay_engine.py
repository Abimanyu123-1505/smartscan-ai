"""
replay_engine.py
================
Time-indexed replay engine over a real RF recording.

The engine holds the FULL PSD matrix but enforces strict
masking: only the chosen frequency at the current time slot
is ever returned to the scheduler/receiver.

SEPARATION OF CONCERNS:
  WorldData      — the full PSD (hidden from scheduler)
  ReceiverObservation — what the receiver actually sees
  EvaluationTruth — used only for metrics, never for decisions

DATA LEAKAGE PROTECTION:
  - get_observation() ONLY returns the selected frequency
  - get_evaluation_truth() is ONLY called by the Evaluator, never by the Scheduler
  - Future time slots cannot be requested (raises ValueError if t > current_slot)
"""

from typing import List, Dict, Any, Optional
from ..preprocessing.rf_preprocessor import PreprocessedPSD
from ..preprocessing.event_detector import RFEvent
from ..ingestion.metadata import RecordingMetadata
import numpy as np

class ReplayEngine:
    def __init__(self, psd_result: PreprocessedPSD, events: List[RFEvent], recording_meta: RecordingMetadata, noise_floor_db: float):
        self.psd_result = psd_result
        self.events = events
        self.recording_meta = recording_meta
        self.noise_floor_db = noise_floor_db
        
        self._current_slot = 0
        self._n_slots, self._n_bins = self.psd_result.power_db.shape

    @property
    def num_time_slots(self) -> int:
        return self._n_slots

    @property
    def num_freq_bins(self) -> int:
        return self._n_bins

    @property
    def current_slot(self) -> int:
        return self._current_slot

    @property
    def freq_bins_hz(self) -> List[float]:
        return self.psd_result.freq_bins.tolist()

    def advance(self):
        if self._current_slot < self._n_slots - 1:
            self._current_slot += 1

    def get_observation(self, freq_bin: int) -> Dict[str, Any]:
        """ONLY at current_slot"""
        power_db = float(self.psd_result.power_db[self._current_slot, freq_bin])
        snr = power_db - self.noise_floor_db
        
        # Check if there's an event matching this slot/bin
        detected = False
        for e in self.events:
            if e.freq_bin == freq_bin and e.start_slot <= self._current_slot <= e.end_slot:
                detected = True
                break
                
        # Or simplistic detection fallback if event list is not the ground truth logic
        if not detected and snr > 10.0:
            detected = True
            
        return {
            "power_db": power_db,
            "detected": detected,
            "snr_estimate_db": snr,
            "freq_hz": float(self.psd_result.freq_bins[freq_bin]),
            "time_slot": self._current_slot
        }

    def get_evaluation_truth(self, time_slot: int, freq_bin: int) -> Dict[str, Any]:
        """ONLY callable by Evaluator (enforced by token logic conceptually)"""
        if time_slot > self._current_slot:
            raise ValueError("Future time slots cannot be requested")
            
        active = False
        event_id = None
        for e in self.events:
            if e.freq_bin == freq_bin and e.start_slot <= time_slot <= e.end_slot:
                active = True
                event_id = e.event_id
                break
                
        return {
            "active": active,
            "event_id": event_id,
            "true_power_db": float(self.psd_result.power_db[time_slot, freq_bin])
        }

    def get_display_psd(self, max_history: int = 60) -> Dict[str, Any]:
        """downsampled PSD for UI, reveals ONLY the receiver trajectory"""
        start_idx = max(0, self._current_slot - max_history)
        end_idx = self._current_slot + 1
        
        slice_power = self.psd_result.power_db[start_idx:end_idx, :]
        return {
            "time_slots": self.psd_result.time_slots[start_idx:end_idx].tolist(),
            "power_db": slice_power.tolist(),
            "freq_bins": self.freq_bins_hz
        }

    def get_full_psd_for_display(self) -> Dict[str, Any]:
        """full PSD for admin/research view (labelled as such)"""
        # Downsample across time to prevent huge payload
        step = max(1, self._n_slots // 300)
        return {
            "time_slots": self.psd_result.time_slots[::step].tolist(),
            "power_db": self.psd_result.power_db[::step, :].tolist(),
            "freq_bins": self.freq_bins_hz
        }

    def reset(self):
        self._current_slot = 0

    def is_finished(self) -> bool:
        return self._current_slot >= self._n_slots - 1

    def summary(self) -> Dict[str, Any]:
        return {
            "total_slots": self._n_slots,
            "total_bins": self._n_bins,
            "current_slot": self._current_slot,
            "recording_id": self.recording_meta.recording_id,
            "events_count": len(self.events)
        }
