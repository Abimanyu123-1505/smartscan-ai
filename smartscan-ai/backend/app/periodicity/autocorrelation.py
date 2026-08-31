import numpy as np

class AutocorrelationEstimator:
    @staticmethod
    def estimate_period(signal, max_lag=100):
        if len(signal) < 2:
            return None
        max_lag = min(max_lag, len(signal) - 1)
        acf = np.correlate(signal - np.mean(signal), signal - np.mean(signal), mode='full')
        acf = acf[len(acf)//2:]
        acf = acf[:max_lag+1]
        
        # Find first peak
        peaks = np.where((acf[1:-1] > acf[:-2]) & (acf[1:-1] > acf[2:]))[0] + 1
        if len(peaks) > 0:
            return peaks[0]
        return None
