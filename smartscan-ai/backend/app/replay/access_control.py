from ..core.exceptions import DataLeakageError

class AccessController:
    def __init__(self, engine):
        self.engine = engine
        
    def check_access(self, requested_t, requested_freqs):
        if requested_t > self.engine.time_index:
            raise DataLeakageError("Time access violation")
        return True
