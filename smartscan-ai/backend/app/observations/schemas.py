from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class ReceiverObservation:
    timestamp: float
    center_freq: float
    bandwidth: float
    data: np.ndarray

@dataclass
class ObservationHistory:
    observations: List[ReceiverObservation]
