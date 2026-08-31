def slice_frequency_window(psd_row, center_idx, width):
    start = max(0, center_idx - width // 2)
    end = min(len(psd_row), center_idx + width // 2)
    return psd_row[start:end]
