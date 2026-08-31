from .base import BaseReceiver

class NarrowbandReplayReceiver(BaseReceiver):
    def __init__(self, bw, tune_delay):
        self.bandwidth = bw
        self.tune_delay = tune_delay
        self.current_freq = 0
        
    def tune(self, frequency):
        cost = self.tune_delay if frequency != self.current_freq else 0
        self.current_freq = frequency
        return cost
