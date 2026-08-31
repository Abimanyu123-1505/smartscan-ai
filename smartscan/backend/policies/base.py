"""
policies/base.py — Abstract base class for all scanning policies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PolicyContext:
    current_slot: int
    current_freq_bin: int
    num_freq_bins: int
    belief_state: Any
    last_observation: Any
    config: Dict[str, Any]

class BasePolicy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def select(self, context: PolicyContext) -> int:
        pass

    def reset(self):
        pass

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description
        }
