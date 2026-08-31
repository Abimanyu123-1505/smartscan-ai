class MultiObjectiveEvaluator:
    def __init__(self, reward_fn, cost_fn):
        self.reward_fn = reward_fn
        self.cost_fn = cost_fn

    def evaluate(self, state, action, result):
        # Result dictionary containing hits, misses, etc.
        reward = self.reward_fn.calculate(result.get('hit', False), result.get('miss', False), 
                                          result.get('false_alarm', False), result.get('switch', False))
        cost = self.cost_fn.calculate(result.get('delay', 0), result.get('pfa', 0), 
                                      result.get('pd', 1), result.get('switches', 0))
        return {'reward': reward, 'cost': cost, 'utility': reward - cost}
