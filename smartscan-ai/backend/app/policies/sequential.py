from .base import BasePolicy

class SequentialPolicy(BasePolicy):
    def __init__(self, action_space):
        super().__init__(action_space)
        self.current_idx = 0

    def select_action(self, state):
        action = self.action_space[self.current_idx]
        self.current_idx = (self.current_idx + 1) % len(self.action_space)
        return action

    def update(self, state, action, reward, next_state):
        pass

    def reset(self):
        self.current_idx = 0

    def get_explanation(self, state, action):
        return f"Selected {action} sequentially."
