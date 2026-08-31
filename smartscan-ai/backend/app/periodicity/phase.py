import numpy as np

class PhaseCalculator:
    @staticmethod
    def calculate_next_event(last_event_time, period):
        if last_event_time is None or period is None:
            return None
        return last_event_time + period
