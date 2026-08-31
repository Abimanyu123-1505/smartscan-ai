from dataclasses import dataclass

@dataclass
class FrequencyBelief:
    freq: float
    alpha: float = 1.0
    beta: float = 1.0
    
class BeliefStateEngine:
    def __init__(self, freqs):
        self.beliefs = {f: FrequencyBelief(f) for f in freqs}
        
    def update(self, freq, activity, weight=0.1):
        if freq in self.beliefs:
            self.beliefs[freq].alpha = self.beliefs[freq].alpha * (1-weight) + activity
            self.beliefs[freq].beta = self.beliefs[freq].beta * (1-weight) + (1-activity)
