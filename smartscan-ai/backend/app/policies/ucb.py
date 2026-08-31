import math
from .base import BasePolicy

class UCBPolicy(BasePolicy):
    def __init__(self, action_space, c=1.414):
        super().__init__(action_space)
        self.c = c
        self.reset()

    def select_action(self, state):
        if self.total_counts == 0:
            return self.action_space[0]
        
        best_action = None
        best_ucb = -float('inf')
        
        for action in self.action_space:
            if self.counts[action] == 0:
                return action
            
            avg_reward = self.values[action] / self.counts[action]
            ucb = avg_reward + self.c * math.sqrt(math.log(self.total_counts) / self.counts[action])
            if ucb > best_ucb:
                best_ucb = ucb
                best_action = action
                
        return best_action

    def update(self, state, action, reward, next_state):
        self.counts[action] += 1
        self.total_counts += 1
        self.values[action] += reward

    def reset(self):
        self.counts = {a: 0 for a in self.action_space}
        self.values = {a: 0.0 for a in self.action_space}
        self.total_counts = 0
