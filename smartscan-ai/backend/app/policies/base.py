from abc import ABC, abstractmethod

class BasePolicy(ABC):
    def __init__(self, action_space):
        self.action_space = action_space

    @abstractmethod
    def select_action(self, state):
        pass

    @abstractmethod
    def update(self, state, action, reward, next_state):
        pass

    @abstractmethod
    def reset(self):
        pass

    def get_state(self):
        return {}

    def get_explanation(self, state, action):
        return "No explanation available."
