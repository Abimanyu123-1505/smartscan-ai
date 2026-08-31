"""
smartscan.backend.app.receiver.base_receiver
=============================================
Hardware Abstraction Layer (HAL) Base Class for SmartScan AI.
Defines unified interface for both Real RF Replay and Live SDR hardware.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class ReceiverObservation:
    time_slot: int
    frequency_bin: int
    frequency_hz: float
    bandwidth_hz: float
    sample_rate_hz: float
    power_db: float
    detected: bool
    confidence: float
    snr_estimate_db: float
    switched: bool
    switch_cost_paid: float
    dwell_slots: int
    masked_frequencies: str = "all_except_selected"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_slot": self.time_slot,
            "frequency_bin": self.frequency_bin,
            "frequency_hz": round(float(self.frequency_hz), 2),
            "bandwidth_hz": round(float(self.bandwidth_hz), 2),
            "sample_rate_hz": round(float(self.sample_rate_hz), 2),
            "power_db": round(float(self.power_db), 2),
            "detected": self.detected,
            "confidence": round(float(self.confidence), 4),
            "snr_estimate_db": round(float(self.snr_estimate_db), 2),
            "switched": self.switched,
            "switch_cost_paid": round(float(self.switch_cost_paid), 4),
            "dwell_slots": self.dwell_slots,
            "masked_frequencies": self.masked_frequencies,
            "timestamp": self.timestamp,
        }


@dataclass
class ReceiverState:
    device_name: str
    is_connected: bool
    current_frequency_hz: float
    sample_rate_hz: float
    bandwidth_hz: float
    gain_db: float
    total_samples: int
    dropped_samples: int
    buffer_health: float
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_name": self.device_name,
            "is_connected": self.is_connected,
            "current_frequency_hz": round(float(self.current_frequency_hz), 2),
            "sample_rate_hz": round(float(self.sample_rate_hz), 2),
            "bandwidth_hz": round(float(self.bandwidth_hz), 2),
            "gain_db": round(float(self.gain_db), 2),
            "total_samples": self.total_samples,
            "dropped_samples": self.dropped_samples,
            "buffer_health": round(float(self.buffer_health), 4),
            "latency_ms": round(float(self.latency_ms), 3),
        }


class BaseReceiver(ABC):
    """
    Abstract interface for all hardware and replay narrowband receivers.
    All policies and ML models operate through this abstraction.
    """

    @abstractmethod
    def tune(self, frequency_hz: float) -> bool:
        """Retunes the receiver to a target frequency in Hz."""
        pass

    @abstractmethod
    def capture(self, num_samples: int) -> Optional[Any]:
        """Captures raw IQ samples from current tuned frequency."""
        pass

    @abstractmethod
    def observe(self, freq_bin: int, time_slot: int) -> ReceiverObservation:
        """Returns narrowband power observation and detection at specified channel/slot."""
        pass

    @abstractmethod
    def get_state(self) -> ReceiverState:
        """Returns current receiver hardware status, sample rate, latency, and health."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Gracefully releases hardware resources."""
        pass
