from ..core.exceptions import DataLeakageError

class ReplayEngine:
    def __init__(self, full_psd_matrix):
        self._full_psd_matrix = full_psd_matrix
        self.time_index = 0
        
    def get_observation(self, t, freq_indices):
        if t > self.time_index:
            raise DataLeakageError(f"Requested time {t} is in the future")
        return self._full_psd_matrix[t, freq_indices]
