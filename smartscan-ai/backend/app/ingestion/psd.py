import numpy as np
from scipy import signal

class PSDReader:
    def __init__(self, nperseg=256):
        self.nperseg = nperseg

    def compute(self, data, fs=1.0):
        f, t, Zxx = signal.stft(data, fs=fs, nperseg=self.nperseg)
        psd = np.abs(Zxx)**2
        return 10 * np.log10(psd + 1e-12)
