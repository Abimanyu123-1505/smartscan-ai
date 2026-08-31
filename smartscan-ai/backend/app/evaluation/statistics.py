import numpy as np
import scipy.stats as st

class MonteCarloStats:
    @staticmethod
    def get_stats(data, confidence=0.95):
        mean = np.mean(data)
        sem = st.sem(data)
        ci = st.t.interval(confidence, len(data)-1, loc=mean, scale=sem)
        return {
            'mean': mean,
            'std': np.std(data),
            'ci_lower': ci[0],
            'ci_upper': ci[1]
        }
