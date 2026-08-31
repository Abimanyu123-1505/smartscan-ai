class ReceiverConstraints:
    def __init__(self, max_bw, min_freq, max_freq):
        self.max_bw = max_bw
        self.min_freq = min_freq
        self.max_freq = max_freq
        
    def is_valid(self, freq, bw):
        return (self.min_freq <= freq <= self.max_freq) and (bw <= self.max_bw)
