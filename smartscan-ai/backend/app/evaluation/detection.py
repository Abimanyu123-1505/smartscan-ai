class DetectionMetrics:
    @staticmethod
    def calculate(tp, fp, tn, fn):
        pd = tp / (tp + fn) if (tp + fn) > 0 else 0
        pfa = fp / (fp + tn) if (fp + tn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * (precision * pd) / (precision + pd) if (precision + pd) > 0 else 0
        
        return {
            'pd': pd,
            'pfa': pfa,
            'precision': precision,
            'f1': f1,
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn
        }
