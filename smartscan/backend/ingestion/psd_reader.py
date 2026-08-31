"""
psd_reader.py — PSD / spectrogram computation from IQ samples
Uses scipy.signal.spectrogram (Welch-based STFT).
Outputs R[time_slot, freq_bin] in dB.
Does NOT modify the underlying measurements.
"""

import numpy as np
from scipy import signal
from typing import Optional
from .iq_reader import IQReader

class PSDResult:
    def __init__(self, time_slots: np.ndarray, freq_bins: np.ndarray, power_db: np.ndarray, sample_rate: float, center_frequency: float, method: str):
        self.time_slots = time_slots
        self.freq_bins = freq_bins
        self.power_db = power_db
        self.sample_rate = sample_rate
        self.center_frequency = center_frequency
        self.method = method

    def to_dict(self) -> dict:
        return {
            "time_slots": self.time_slots.tolist(),
            "freq_bins": self.freq_bins.tolist(),
            "power_db": self.power_db.tolist(),
            "sample_rate": self.sample_rate,
            "center_frequency": self.center_frequency,
            "method": self.method
        }

    def freq_bin_for(self, target_hz: float) -> int:
        idx = np.abs(self.freq_bins - target_hz).argmin()
        return int(idx)

    def slice_freq_range(self, f_start: float, f_end: float) -> 'PSDResult':
        mask = (self.freq_bins >= f_start) & (self.freq_bins <= f_end)
        return PSDResult(
            time_slots=self.time_slots,
            freq_bins=self.freq_bins[mask],
            power_db=self.power_db[:, mask],
            sample_rate=self.sample_rate,
            center_frequency=self.center_frequency,
            method=self.method
        )

class PSDReader:
    def __init__(self, sample_rate: float, nperseg: int = 1024, noverlap: Optional[int] = None, window: str = 'hann', freq_bins: Optional[int] = None):
        self.sample_rate = sample_rate
        self.nperseg = nperseg
        self.noverlap = noverlap if noverlap is not None else nperseg // 2
        self.window = window
        self.freq_bins = freq_bins

    def compute(self, iq_samples: np.ndarray) -> PSDResult:
        f, t, Sxx = signal.spectrogram(
            iq_samples,
            fs=self.sample_rate,
            window=self.window,
            nperseg=self.nperseg,
            noverlap=self.noverlap,
            return_onesided=False,
            mode='psd'
        )
        
        f = np.fft.fftshift(f)
        Sxx = np.fft.fftshift(Sxx, axes=0)
        
        power_db = 10 * np.log10(np.clip(Sxx, a_min=1e-15, a_max=None))
        power_db = power_db.T  # Shape: [time_slots, freq_bins]
        
        return PSDResult(
            time_slots=t,
            freq_bins=f,
            power_db=power_db,
            sample_rate=self.sample_rate,
            center_frequency=0.0,
            method="scipy.signal.spectrogram"
        )

    def compute_from_file(self, reader: IQReader, start_sample: int = 0, max_samples: Optional[int] = None) -> PSDResult:
        iq_samples = reader.read(start_sample=start_sample, n_samples=max_samples)
        psd_res = self.compute(iq_samples)
        psd_res.center_frequency = reader.center_freq
        psd_res.freq_bins += reader.center_freq
        return psd_res

    def downsample_for_display(self, psd_result: PSDResult, max_time_slots: int = 300, max_freq_bins: int = 256) -> PSDResult:
        power_db = psd_result.power_db
        t_slots, f_bins = power_db.shape
        
        t_step = max(1, t_slots // max_time_slots)
        f_step = max(1, f_bins // max_freq_bins)
        
        downsampled_power = power_db[::t_step, ::f_step]
        downsampled_t = psd_result.time_slots[::t_step]
        downsampled_f = psd_result.freq_bins[::f_step]
        
        return PSDResult(
            time_slots=downsampled_t,
            freq_bins=downsampled_f,
            power_db=downsampled_power,
            sample_rate=psd_result.sample_rate,
            center_frequency=psd_result.center_frequency,
            method=f"{psd_result.method}_downsampled"
        )
