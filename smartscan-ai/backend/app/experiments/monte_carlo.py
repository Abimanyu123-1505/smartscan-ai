class MonteCarloEvaluator:
    def __init__(self, num_seeds=10):
        self.num_seeds = num_seeds
        
    def evaluate(self, experiment_fn):
        results = []
        for seed in range(self.num_seeds):
            res = experiment_fn(seed)
            results.append(res)
        return results
