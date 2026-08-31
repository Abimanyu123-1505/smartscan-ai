from scipy import signal

def compute_stft(data, fs=1.0, nperseg=256):
    f, t, Zxx = signal.stft(data, fs=fs, nperseg=nperseg)
    return f, t, Zxx
