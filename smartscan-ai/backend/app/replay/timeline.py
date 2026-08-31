class TimelineTracker:
    def __init__(self):
        self.current_time = 0
        
    def advance(self, dt=1):
        self.current_time += dt
