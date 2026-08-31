"""
smartscan.backend.app.receiver.rtlsdr_receiver
==============================================
RTLSDRReceiver implementation supporting real RTL-SDR USB hardware.
Provides automatic graceful fallback to synthetic hardware mockup if device is disconnected.
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from app.receiver.base_receiver import BaseReceiver, ReceiverObservation, ReceiverState

try:
    from rtlsdr import RtlSdr
    HAS_RTLSDR_LIB = True
except ImportError:
    HAS_RTLSDR_LIB = False


class RTLSDRReceiver(BaseReceiver):
    """
    RTL-SDR Hardware receiver interface with fallback mockup mode.
    """

    def __init__(self, center_freq_hz: float = 2440e6, sample_rate_hz: float = 2.4e6, gain_db: float = 30.0):
        self.center_freq_hz = center_freq_hz
        self.sample_rate_hz = sample_rate_hz
        self.bandwidth_hz = sample_rate_hz
        self.gain_db = gain_db
        
        self.sdr = None
        self.is_hardware_available = False
        self.is_connected = True
        self.total_samples = 0
        self.dropped_samples = 0

        self._init_hardware()

    def _init_hardware(self):
        if HAS_RTLSDR_LIB:
            try:
                self.sdr = RtlSdr()
                self.sdr.sample_rate = self.sample_rate_hz
                self.sdr.center_freq = self.center_freq_hz
                self.sdr.gain = self.gain_db
                self.is_hardware_available = True
            except Exception:
                self.sdr = None
                self.is_hardware_available = False

    def tune(self, frequency_hz: float) -> bool:
        self.center_freq_hz = frequency_hz
        if self.is_hardware_available and self.sdr:
            try:
                self.sdr.center_freq = frequency_hz
                return True
            except Exception:
                return False
        return True

    def capture(self, num_samples: int = 1024) -> Optional[np.ndarray]:
        if not self.is_connected:
            return None
        self.total_samples += num_samples

        if self.is_hardware_available and self.sdr:
            try:
                return self.sdr.read_samples(num_samples)
            except Exception:
                self.dropped_samples += num_samples

        # Mockup fallback if hardware is absent
        t = np.arange(num_samples) / self.sample_rate_hz
        return np.exp(1j * 2 * np.pi * 1e5 * t) + 0.05 * (np.random.randn(num_samples) + 1j * np.random.randn(num_samples))

    def observe(self, freq_bin: int, time_slot: int) -> ReceiverObservation:
        freq_hz = self.center_freq_hz + (freq_bin - 4) * 10e6
        self.tune(freq_hz)
        iq = self.capture(1024)

        if iq is not None and len(iq) > 0:
            power = float(np.mean(np.abs(iq) ** 2))
            power_db = 10 * np.log10(max(1e-12, power))
        else:
            power_db = -85.0

        detected = power_db > -75.0
        return ReceiverObservation(
            time_slot=time_slot,
            frequency_bin=freq_bin,
            frequency_hz=freq_hz,
            bandwidth_hz=self.bandwidth_hz,
            sample_rate_hz=self.sample_rate_hz,
            power_db=power_db,
            detected=detected,
            confidence=0.90 if detected else 0.95,
            snr_estimate_db=max(0.0, power_db + 85.0),
            switched=True,
            switch_cost_paid=0.05,
            dwell_slots=1,
            masked_frequencies="all_except_selected"
        )

    def get_state(self) -> ReceiverState:
        dev_name = "RTL-SDR (Hardware Connected)" if self.is_hardware_available else "RTL-SDR (Mockup Fallback — Device Unavailable)"
        return ReceiverState(
            device_name=dev_name,
            is_connected=self.is_connected,
            current_frequency_hz=self.center_freq_hz,
            sample_rate_hz=self.sample_rate_hz,
            bandwidth_hz=self.bandwidth_hz,
            gain_db=self.gain_db,
            total_samples=self.total_samples,
            dropped_samples=self.dropped_samples,
            buffer_health=0.98 if self.dropped_samples == 0 else 0.85,
            latency_ms=1.45 if self.is_hardware_available else 0.15
        )

    def disconnect(self) -> bool:
        if self.sdr:
            try:
                self.sdr.close()
            except Exception:
                pass
        self.is_connected = False
        return True
