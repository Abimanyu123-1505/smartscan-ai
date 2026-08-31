def calculate_tuning_cost(f_start, f_end, cost_per_mhz=0.1):
    return abs(f_end - f_start) * cost_per_mhz
