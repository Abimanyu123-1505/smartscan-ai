def split_temporal(data, test_ratio=0.2):
    split_idx = int(len(data) * (1 - test_ratio))
    return data[:split_idx], data[split_idx:]
