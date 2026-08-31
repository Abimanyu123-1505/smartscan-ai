import random
from typing import Optional
from .base import BasePolicy, PolicyContext

class RandomPolicy(BasePolicy):
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    @property
    def name(self) -> str:
        return 'random'

    @property
    def description(self) -> str:
        return 'Uniform random scan. Selects any frequency with equal probability. Provides a stochastic baseline with no memory.'

    def select(self, context: PolicyContext) -> int:
        return random.randint(0, context.num_freq_bins - 1)

    def reset(self):
        if self.seed is not None:
            random.seed(self.seed)
