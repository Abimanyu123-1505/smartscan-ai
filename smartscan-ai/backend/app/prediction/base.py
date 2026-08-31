"""
smartscan.backend.app.prediction.base
=====================================
Base interfaces, task definitions, and result structures for ML predictors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import time
import numpy as np


class PredictionTask(str, Enum):
    TASK_A_BINARY_ACTIVITY = "TASK_A_BINARY_ACTIVITY"       # Y[t, f] in {0, 1}
    TASK_B_FUTURE_ACTIVITY = "TASK_B_FUTURE_ACTIVITY"       # Y[t+h, f] in {0, 1}
    TASK_C_EVENT_PREDICTION = "TASK_C_EVENT_PREDICTION"     # P(event in [t, t+H])
    TASK_D_EVENT_TIMING     = "TASK_D_EVENT_TIMING"         # T_next (slots until next burst)


@dataclass
class PredictionResult:
    prediction_id: str
    model_name: str
    model_version: str
    dataset_id: str
    recording_id: str
    timestamp_slot: int
    frequency_bin: int
    horizon_step: int
    probability: float
    binary_prediction: int
    confidence: float
    inference_latency_ms: float
    feature_version: str = "v1.0"
    
    # Extended matrix fields for multi-frequency / multi-horizon
    probability_by_frequency: List[float] = field(default_factory=list)
    probability_by_time: List[float] = field(default_factory=list)
    probability_matrix: Optional[List[List[float]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "dataset_id": self.dataset_id,
            "recording_id": self.recording_id,
            "timestamp_slot": self.timestamp_slot,
            "frequency_bin": self.frequency_bin,
            "horizon_step": self.horizon_step,
            "probability": round(float(self.probability), 4),
            "binary_prediction": int(self.binary_prediction),
            "confidence": round(float(self.confidence), 4),
            "inference_latency_ms": round(float(self.inference_latency_ms), 3),
            "feature_version": self.feature_version,
            "probability_by_frequency": [round(float(p), 4) for p in self.probability_by_frequency],
            "probability_by_time": [round(float(p), 4) for p in self.probability_by_time],
        }


class BasePredictor(ABC):
    """
    Abstract interface for all SmartScan AI activity and spectrum prediction models.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def task(self) -> PredictionTask:
        pass

    @abstractmethod
    def fit(self, dataset: Any) -> Dict[str, Any]:
        """Fit model parameters on training dataset split."""
        pass

    @abstractmethod
    def predict(self, input_features: Any) -> int:
        """Return binary prediction (0 or 1)."""
        pass

    @abstractmethod
    def predict_proba(self, input_features: Any) -> float:
        """Return predicted probability P(active)."""
        pass

    @abstractmethod
    def evaluate(self, test_dataset: Any) -> Dict[str, Any]:
        """Evaluate model performance on test dataset split."""
        pass

    @abstractmethod
    def save(self, path: str) -> bool:
        """Save model parameters to disk."""
        pass

    @abstractmethod
    def load(self, path: str) -> bool:
        """Load model parameters from disk."""
        pass

    def metadata(self) -> Dict[str, Any]:
        return {
            "model_name": self.name,
            "model_version": self.version,
            "prediction_task": self.task.value,
        }
