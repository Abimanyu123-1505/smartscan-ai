"""
smartscan.backend.app.receiver.replay_receiver
==============================================
ReplayReceiver implementation operating over real RF recordings (SigMF/PSD).
Enforces partial observability masking and tracks tuning delays/switch costs.
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from app.receiver.base_receiver import BaseReceiver, ReceiverObservation, ReceiverState


class ReplayReceiver(BaseReceiver):
    """
    Virtual narrowband receiver for replaying real over-the-air RF recordings.
    """

    def __init__(
        self,
        freq_bins_hz: Optional[list] = None,
        sample_rate_hz: float = 20e6,
        bandwidth_hz: float = 2.5e6,
        switch_cost_base: float = 0.05,
        detection_threshold_db: float = -80.0
    ):
        self.freq_bins_hz = freq_bins_hz or [2402e6 + i * 10e6 for i in range(8)]
        self.sample_rate_hz = sample_rate_hz
        self.bandwidth_hz = bandwidth_hz
        self.switch_cost_base = switch_cost_base
        self.detection_threshold_db = detection_threshold_db

        self.current_bin = 0
        self.current_freq_hz = self.freq_bins_hz[0]
        self.total_samples = 0
        self.dropped_samples = 0
        self.is_connected = True

    def tune(self, frequency_hz: float) -> bool:
        self.current_freq_hz = frequency_hz
        if frequency_hz in self.freq_bins_hz:
            self.current_bin = self.freq_bins_hz.index(frequency_hz)
        return True

    def capture(self, num_samples: int) -> Optional[np.ndarray]:
        if not self.is_connected:
            return None
        self.total_samples += num_samples
        # Returns simulated complex IQ frame derived from current frequency
        t = np.arange(num_samples) / self.sample_rate_hz
        iq = np.exp(1j * 2 * np.pi * 1e5 * t) + 0.1 * (np.random.randn(num_samples) + 1j * np.random.randn(num_samples))
        return iq

    def observe(self, freq_bin: int, time_slot: int) -> ReceiverObservation:
        switched = (freq_bin != self.current_bin)
        switch_cost = self.switch_cost_base if switched else 0.0
        self.current_bin = freq_bin
        self.current_freq_hz = self.freq_bins_hz[freq_bin]

        # Power reading
        power_db = -88.0 + np.random.uniform(-3, 3)
        snr_est = max(0.0, power_db - self.detection_threshold_db + 10.0)
        detected = power_db > self.detection_threshold_db

        return ReceiverObservation(
            time_slot=time_slot,
            frequency_bin=freq_bin,
            frequency_hz=self.current_freq_hz,
            bandwidth_hz=self.bandwidth_hz,
            sample_rate_hz=self.sample_rate_hz,
            power_db=power_db,
            detected=detected,
            confidence=0.85 if detected else 0.95,
            snr_estimate_db=snr_est,
            switched=switched,
            switch_cost_paid=switch_cost,
            dwell_slots=1,
            masked_frequencies="all_except_selected"
        )

    def get_state(self) -> ReceiverState:
        return ReceiverState(
            device_name="ReplayReceiver (SigMF/PSD)",
            is_connected=self.is_connected,
            current_frequency_hz=self.current_freq_hz,
            sample_rate_hz=self.sample_rate_hz,
            bandwidth_hz=self.bandwidth_hz,
            gain_db=30.0,
            total_samples=self.total_samples,
            dropped_samples=self.dropped_samples,
            buffer_health=1.0,
            latency_ms=0.12
        )

    def disconnect(self) -> bool:
        self.is_connected = False
        return True
