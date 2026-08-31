import numpy as np

class CalibrationEngine:
    @staticmethod
    def brier_score(y_true, y_prob):
        return np.mean((y_prob - y_true) ** 2)

    @staticmethod
    def reliability_diagram(y_true, y_prob, n_bins=10):
        bins = np.linspace(0., 1., n_bins + 1)
        binids = np.digitize(y_prob, bins) - 1
        bin_sums = np.bincount(binids, weights=y_prob, minlength=len(bins))
        bin_true = np.bincount(binids, weights=y_true, minlength=len(bins))
        bin_total = np.bincount(binids, minlength=len(bins))
        
        nonzero = bin_total != 0
        prob_pred = bin_sums[nonzero] / bin_total[nonzero]
        prob_true = bin_true[nonzero] / bin_total[nonzero]
        
        return prob_pred, prob_true
