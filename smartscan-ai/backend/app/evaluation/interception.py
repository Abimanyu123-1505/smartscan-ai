import numpy as np

class InterceptionMetrics:
    @staticmethod
    def calculate(total_events, intercepted_events, intercept_times):
        ir = intercepted_events / total_events if total_events > 0 else 0
        
        metrics = {'interception_rate': ir}
        if intercept_times:
            metrics['mean_time'] = np.mean(intercept_times)
            metrics['median_time'] = np.median(intercept_times)
            metrics['p95_time'] = np.percentile(intercept_times, 95)
        else:
            metrics['mean_time'] = None
            metrics['median_time'] = None
            metrics['p95_time'] = None
            
        return metrics
