import random
from .base import BasePolicy

class RandomPolicy(BasePolicy):
    def select_action(self, state):
        return random.choice(self.action_space)

    def update(self, state, action, reward, next_state):
        pass

    def reset(self):
        pass

    def get_explanation(self, state, action):
        return f"Selected {action} randomly."
