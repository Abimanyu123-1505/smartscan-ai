import numpy as np

class FFTEstimator:
    @staticmethod
    def estimate_period(signal, fs=1.0):
        if len(signal) < 2:
            return None
        fft_vals = np.fft.fft(signal - np.mean(signal))
        fft_freqs = np.fft.fftfreq(len(signal), d=1/fs)
        
        pos_freqs = fft_freqs[fft_freqs > 0]
        pos_vals = np.abs(fft_vals[fft_freqs > 0])
        
        if len(pos_freqs) == 0:
            return None
            
        peak_freq = pos_freqs[np.argmax(pos_vals)]
        if peak_freq > 0:
            return 1.0 / peak_freq
        return None
