from .base import BasePolicy

class GreedyPredictivePolicy(BasePolicy):
    def __init__(self, action_space, predictor):
        super().__init__(action_space)
        self.predictor = predictor

    def select_action(self, state):
        # State should contain features for predictor
        # For simplicity, assume state is a list of features per action
        best_action = None
        best_prob = -1
        for action in self.action_space:
            features = state.get(action, [])
            if not features:
                continue
            prob = self.predictor.predict_proba([features])[0][1] # Assuming binary, class 1 is event
            if prob > best_prob:
                best_prob = prob
                best_action = action
        return best_action if best_action is not None else self.action_space[0]

    def update(self, state, action, reward, next_state):
        pass # Predictor trained offline or via its own mechanism

    def reset(self):
        pass
