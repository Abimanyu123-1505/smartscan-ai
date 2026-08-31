from .base import BasePolicy, PolicyContext

class SequentialPolicy(BasePolicy):
    @property
    def name(self) -> str:
        return 'sequential'

    @property
    def description(self) -> str:
        return 'Fixed sequential scan. Cycles through all frequency bins in order. Baseline policy — no adaptation.'

    def select(self, context: PolicyContext) -> int:
        return (context.current_freq_bin + 1) % context.num_freq_bins
