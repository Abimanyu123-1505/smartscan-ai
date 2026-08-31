def extract_features(obs_history):
    return [obs.center_freq for obs in obs_history]
