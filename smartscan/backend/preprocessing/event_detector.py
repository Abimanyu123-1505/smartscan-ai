"""
event_detector.py
=================
Detects RF emission events from measured PSD.

All detections are DERIVED from measured data.
Never claim these are ground-truth emitter labels.
Call them 'derived_occupancy' or 'measurement_derived_event'.

IMPORTANT TERMINOLOGY:
  - 'measured activity'  : power above threshold in R[t,f]
  - 'derived_occupancy'  : O[t,f] = 1 if measured activity > threshold
  - 'annotated_event'    : only if dataset provides annotations
  - 'ground_truth'       : never used for derived labels
"""

import uuid
import numpy as np
from typing import List, Optional
from ..ingestion.psd_reader import PSDResult

class RFEvent:
    def __init__(self, recording_id: str, freq_bin: int, freq_hz: float, start_slot: int, end_slot: int, peak_power_db: float, mean_power_db: float):
        self.event_id = str(uuid.uuid4())
        self.recording_id = recording_id
        self.freq_bin = freq_bin
        self.freq_hz = freq_hz
        self.start_slot = start_slot
        self.end_slot = end_slot
        self.duration_slots = end_slot - start_slot + 1
        self.peak_power_db = peak_power_db
        self.mean_power_db = mean_power_db
        self.annotation_source = 'measurement_derived'

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "recording_id": self.recording_id,
            "freq_bin": self.freq_bin,
            "freq_hz": self.freq_hz,
            "start_slot": self.start_slot,
            "end_slot": self.end_slot,
            "duration_slots": self.duration_slots,
            "peak_power_db": self.peak_power_db,
            "mean_power_db": self.mean_power_db,
            "annotation_source": self.annotation_source
        }

class EnergyDetector:
    def __init__(self, threshold_db: Optional[float] = None, cfar_guard: int = 2, cfar_train: int = 8, pfa_target: float = 1e-3):
        self.threshold_db = threshold_db
        self.cfar_guard = cfar_guard
        self.cfar_train = cfar_train
        self.pfa_target = pfa_target

    def set_threshold_from_noise_floor(self, noise_floor_db: float, margin_db: float = 6.0):
        self.threshold_db = noise_floor_db + margin_db

    def detect(self, psd_result: PSDResult, freq_bin: int) -> np.ndarray:
        """per-time detection for ONE frequency bin"""
        power_series = psd_result.power_db[:, freq_bin]
        
        if self.threshold_db is not None:
            return power_series > self.threshold_db
            
        # Basic CFAR 1D along time if threshold is not set
        n = len(power_series)
        detections = np.zeros(n, dtype=bool)
        
        alpha = self.cfar_train * (self.pfa_target ** (-1.0 / self.cfar_train) - 1)
        
        for i in range(n):
            left_start = max(0, i - self.cfar_guard - self.cfar_train)
            left_end = max(0, i - self.cfar_guard)
            right_start = min(n, i + self.cfar_guard + 1)
            right_end = min(n, i + self.cfar_guard + self.cfar_train + 1)
            
            train_cells = []
            if left_end > left_start:
                train_cells.extend(power_series[left_start:left_end])
            if right_end > right_start:
                train_cells.extend(power_series[right_start:right_end])
                
            if not train_cells:
                continue
                
            noise_level = np.mean(train_cells)
            if power_series[i] > noise_level + alpha: # Using additive threshold in dB
                detections[i] = True
                
        return detections

    def detect_all(self, psd_result: PSDResult) -> np.ndarray:
        """shape [time, freq] occupancy matrix"""
        n_t, n_f = psd_result.power_db.shape
        occupancy = np.zeros((n_t, n_f), dtype=bool)
        
        if self.threshold_db is not None:
            occupancy = psd_result.power_db > self.threshold_db
            return occupancy
            
        for f in range(n_f):
            occupancy[:, f] = self.detect(psd_result, f)
            
        return occupancy

    def extract_events(self, occupancy: np.ndarray, psd_result: PSDResult, recording_id: str = "unknown") -> List[RFEvent]:
        events = []
        n_t, n_f = occupancy.shape
        
        for f in range(n_f):
            in_event = False
            start_slot = -1
            
            for t in range(n_t):
                if occupancy[t, f] and not in_event:
                    in_event = True
                    start_slot = t
                elif not occupancy[t, f] and in_event:
                    in_event = False
                    end_slot = t - 1
                    
                    power_slice = psd_result.power_db[start_slot:end_slot+1, f]
                    events.append(RFEvent(
                        recording_id=recording_id,
                        freq_bin=f,
                        freq_hz=float(psd_result.freq_bins[f]),
                        start_slot=start_slot,
                        end_slot=end_slot,
                        peak_power_db=float(np.max(power_slice)),
                        mean_power_db=float(np.mean(power_slice))
                    ))
                    
            if in_event:
                end_slot = n_t - 1
                power_slice = psd_result.power_db[start_slot:end_slot+1, f]
                events.append(RFEvent(
                    recording_id=recording_id,
                    freq_bin=f,
                    freq_hz=float(psd_result.freq_bins[f]),
                    start_slot=start_slot,
                    end_slot=end_slot,
                    peak_power_db=float(np.max(power_slice)),
                    mean_power_db=float(np.mean(power_slice))
                ))
                
        return events
