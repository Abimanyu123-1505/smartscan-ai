import numpy as np

def vectorize_belief_state(beliefs):
    vec = []
    for f, b in sorted(beliefs.items()):
        vec.append(b.alpha / (b.alpha + b.beta))
    return np.array(vec)
