"""
replay_receiver.py
==================
Virtual narrowband receiver operating over real RF recordings.

CORE CONSTRAINT:
  The receiver may access ONLY ONE frequency window at each time slot.
  All other frequencies are MASKED.
  This enforces the partial-observability condition.

DATA LEAKAGE PROTECTION:
  The receiver object never holds a reference to the full PSD matrix.
  It holds only a reference to the ReplayEngine which implements masking.
  Future time slots are NEVER accessible.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ReceiverConfig:
    instantaneous_bandwidth_bins: int = 1
    dwell_slots: int = 1
    tuning_delay_slots: int = 1
    switch_cost: float = 0.05
    detection_threshold_db: Optional[float] = None

@dataclass
class ReceiverObservation:
    time_slot: int
    frequency_bin: int
    frequency_hz: float
    power_db: float
    detected: bool
    confidence: float
    snr_estimate_db: float
    switched: bool
    switch_cost_paid: float
    dwell_count: int
    masked_frequencies: str = 'all_except_selected'

    def to_dict(self) -> dict:
        return {
            "time_slot": self.time_slot,
            "frequency_bin": self.frequency_bin,
            "frequency_hz": self.frequency_hz,
            "power_db": self.power_db,
            "detected": self.detected,
            "confidence": self.confidence,
            "snr_estimate_db": self.snr_estimate_db,
            "switched": self.switched,
            "switch_cost_paid": self.switch_cost_paid,
            "dwell_count": self.dwell_count,
            "masked_frequencies": self.masked_frequencies
        }

class ReplayReceiver:
    def __init__(self, config: ReceiverConfig, engine: 'ReplayEngine'):
        self.config = config
        self.engine = engine
        self._current_frequency_bin = 0
        self._observation_count = 0
        self._dwell_count = 0

    @property
    def current_frequency_bin(self) -> int:
        return self._current_frequency_bin

    @property
    def current_frequency_hz(self) -> float:
        return self.engine.freq_bins_hz[self._current_frequency_bin]

    @property
    def observation_count(self) -> int:
        return self._observation_count

    def _compute_confidence(self, power_db: float, noise_floor_db: float) -> float:
        snr = power_db - noise_floor_db
        if snr < 0:
            return 0.0
        elif snr > 20:
            return 1.0
        return snr / 20.0

    def select_frequency(self, freq_bin: int) -> ReceiverObservation:
        switched = (freq_bin != self._current_frequency_bin)
        
        if switched:
            self._current_frequency_bin = freq_bin
            self._dwell_count = 1
        else:
            self._dwell_count += 1
            
        return self.observe(switched=switched)

    def observe(self, switched: bool = False) -> ReceiverObservation:
        obs_data = self.engine.get_observation(self._current_frequency_bin)
        
        nf = self.engine.noise_floor_db
        confidence = self._compute_confidence(obs_data['power_db'], nf)
        
        obs = ReceiverObservation(
            time_slot=obs_data['time_slot'],
            frequency_bin=self._current_frequency_bin,
            frequency_hz=obs_data['freq_hz'],
            power_db=obs_data['power_db'],
            detected=obs_data['detected'],
            confidence=confidence,
            snr_estimate_db=obs_data['snr_estimate_db'],
            switched=switched,
            switch_cost_paid=self.config.switch_cost if switched else 0.0,
            dwell_count=self._dwell_count
        )
        
        self._observation_count += 1
        return obs

    def reset(self):
        self._current_frequency_bin = 0
        self._observation_count = 0
        self._dwell_count = 0
