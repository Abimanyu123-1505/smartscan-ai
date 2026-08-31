from abc import ABC, abstractmethod

class BaseUncertaintyEngine(ABC):
    @abstractmethod
    def calculate_uncertainty(self, probs):
        pass
