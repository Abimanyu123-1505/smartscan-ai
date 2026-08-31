from abc import ABC, abstractmethod

class BaseReceiver(ABC):
    @abstractmethod
    def tune(self, frequency):
        pass
