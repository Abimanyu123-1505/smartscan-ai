"""
rf_preprocessor.py
==================
Cleans PSD / IQ data for use in the replay engine.
All operations are transparent and logged.
Physically meaningful variations (e.g., true power differences)
are PRESERVED — we only remove known measurement artefacts.
"""

import numpy as np
from typing import List, Tuple
from ..ingestion.psd_reader import PSDResult

class PreprocessedPSD(PSDResult):
    def __init__(self, base_result: PSDResult, operations_applied: List[str], noise_floor_db: float, bad_segments: List[int], original_shape: Tuple[int, ...]):
        super().__init__(
            time_slots=base_result.time_slots,
            freq_bins=base_result.freq_bins,
            power_db=base_result.power_db,
            sample_rate=base_result.sample_rate,
            center_frequency=base_result.center_frequency,
            method=base_result.method
        )
        self.operations_applied = operations_applied
        self.noise_floor_db = noise_floor_db
        self.bad_segments = bad_segments
        self.original_shape = original_shape

class RFPreprocessor:
    def __init__(self, remove_dc: bool = True, normalize: bool = False, clip_floor_db: float = -120.0, clip_ceiling_db: float = 20.0):
        self.remove_dc = remove_dc
        self.normalize = normalize
        self.clip_floor_db = clip_floor_db
        self.clip_ceiling_db = clip_ceiling_db

    def estimate_noise_floor(self, psd_result: PSDResult, percentile: float = 10.0) -> float:
        """noise floor estimate in dB"""
        return float(np.percentile(psd_result.power_db, percentile))

    def detect_bad_segments(self, psd_result: PSDResult, std_multiplier: float = 4.0) -> List[int]:
        """returns time indices with anomalously high/low power"""
        power_means = np.mean(psd_result.power_db, axis=1)
        global_mean = np.mean(power_means)
        global_std = np.std(power_means)
        
        upper_bound = global_mean + std_multiplier * global_std
        lower_bound = global_mean - std_multiplier * global_std
        
        bad_indices = np.where((power_means > upper_bound) | (power_means < lower_bound))[0]
        return bad_indices.tolist()

    def process(self, psd_result: PSDResult) -> PreprocessedPSD:
        """applies DC estimate removal (zero-freq bin), clipping, optional normalization"""
        operations = []
        power_db = psd_result.power_db.copy()
        
        if self.remove_dc:
            # Assuming center frequency is 0 Hz in relative coordinates, or absolute center
            zero_bin = psd_result.freq_bin_for(psd_result.center_frequency)
            
            # Interpolate from neighbors
            if 0 < zero_bin < len(psd_result.freq_bins) - 1:
                power_db[:, zero_bin] = (power_db[:, zero_bin - 1] + power_db[:, zero_bin + 1]) / 2.0
            operations.append("remove_dc")
            
        power_db = np.clip(power_db, a_min=self.clip_floor_db, a_max=self.clip_ceiling_db)
        operations.append(f"clip_db[{self.clip_floor_db},{self.clip_ceiling_db}]")
        
        if self.normalize:
            nf = self.estimate_noise_floor(psd_result)
            power_db = power_db - nf
            operations.append("normalize_to_noise_floor")
            
        bad_segments = self.detect_bad_segments(psd_result)
        if bad_segments:
            operations.append(f"detected_{len(bad_segments)}_bad_segments")
            
        result_copy = PSDResult(
            time_slots=psd_result.time_slots,
            freq_bins=psd_result.freq_bins,
            power_db=power_db,
            sample_rate=psd_result.sample_rate,
            center_frequency=psd_result.center_frequency,
            method=psd_result.method
        )
            
        return PreprocessedPSD(
            base_result=result_copy,
            operations_applied=operations,
            noise_floor_db=self.estimate_noise_floor(psd_result),
            bad_segments=bad_segments,
            original_shape=power_db.shape
        )
