import random
from .base import BasePolicy

class ThompsonSamplingPolicy(BasePolicy):
    def __init__(self, action_space):
        super().__init__(action_space)
        self.reset()

    def select_action(self, state):
        best_action = None
        max_sample = -1
        for action in self.action_space:
            a = self.successes[action] + 1
            b = self.failures[action] + 1
            sample = random.betavariate(a, b)
            if sample > max_sample:
                max_sample = sample
                best_action = action
        return best_action

    def update(self, state, action, reward, next_state):
        if reward > 0:
            self.successes[action] += 1
        else:
            self.failures[action] += 1

    def reset(self):
        self.successes = {a: 0 for a in self.action_space}
        self.failures = {a: 0 for a in self.action_space}
