class EnergyDetector:
    def __init__(self, threshold):
        self.threshold = threshold
        
    def detect(self, signal_power):
        return signal_power > self.threshold
        
class CFARDetector:
    def __init__(self, pfa=1e-3):
        self.pfa = pfa
        
    def detect(self, signal, bg):
        return signal > bg * 1.5
