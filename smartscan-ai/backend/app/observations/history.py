from collections import deque
from .schemas import ReceiverObservation

class ObservationBuffer:
    def __init__(self, maxlen=1000):
        self.buffer = deque(maxlen=maxlen)
        
    def add(self, obs: ReceiverObservation):
        self.buffer.append(obs)
