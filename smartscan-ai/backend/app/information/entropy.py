import numpy as np

def shannon_entropy(probs):
    probs = np.clip(probs, 1e-9, 1 - 1e-9)
    return -np.sum(probs * np.log2(probs), axis=-1)
