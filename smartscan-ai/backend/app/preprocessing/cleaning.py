import numpy as np

def remove_dc(data):
    return data - np.mean(data)

def remove_outliers(data, threshold=3.0):
    mean = np.mean(data)
    std = np.std(data)
    mask = np.abs(data - mean) < threshold * std
    return data * mask
