class PeriodicityTracker:
    def __init__(self):
        self.frequencies = {}
        
    def update(self, freq, event_time):
        if freq not in self.frequencies:
            self.frequencies[freq] = []
        self.frequencies[freq].append(event_time)
        
    def get_history(self, freq):
        return self.frequencies.get(freq, [])
