import numpy as np

class BootstrapConfidence:
    @staticmethod
    def calculate(data, num_samples=1000, alpha=0.05):
        samples = np.random.choice(data, (num_samples, len(data)), replace=True)
        means = np.mean(samples, axis=1)
        return np.percentile(means, [alpha/2 * 100, (1 - alpha/2) * 100])
