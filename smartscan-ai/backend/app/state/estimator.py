class ActivityEstimator:
    def __init__(self, belief_engine):
        self.engine = belief_engine
        
    def estimate_prob(self, freq):
        b = self.engine.beliefs.get(freq)
        if b:
            return b.alpha / (b.alpha + b.beta)
        return 0.5
