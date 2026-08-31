import numpy as np

def compute_psd(stft_data):
    psd = np.abs(stft_data)**2
    return 10 * np.log10(psd + 1e-12)
