import numpy as np

def power_normalize(data):
    mean = np.mean(data)
    std = np.std(data)
    if std > 0:
        return (data - mean) / std
    return data - mean
