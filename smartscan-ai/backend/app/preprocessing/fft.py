import numpy as np

def compute_fft(data):
    return np.fft.fftshift(np.fft.fft(data))
