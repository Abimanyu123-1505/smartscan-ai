import numpy as np

class PredictionMetrics:
    @staticmethod
    def calculate(y_true, y_pred, y_prob=None):
        acc = np.mean(y_true == y_pred)
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(np.mean((y_true - y_pred)**2))
        
        metrics = {
            'accuracy': acc,
            'mae': mae,
            'rmse': rmse
        }
        
        if y_prob is None:
            metrics['brier_score'] = np.mean((y_prob - y_true)**2)
            
        return metrics
