"""
iq_reader.py — Raw complex IQ file reader
Supports: .bin, .iq, .dat, .raw with configurable dtype
Does NOT synthesize or modify data.
"""

import numpy as np
from pathlib import Path
from typing import Union, Optional

class IQReader:
    def __init__(self, path: Union[str, Path], dtype: str = 'complex64', sample_rate: float = 1e6, center_freq: float = 0.0):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"IQ data file not found: {self.path}")
            
        self.dtype_str = dtype
        self.sample_rate = sample_rate
        self.center_freq = center_freq
        
        self.np_dtype = self._parse_dtype(dtype)

    def _parse_dtype(self, dtype: str) -> np.dtype:
        if dtype in ['complex64', 'complex128']:
            return np.dtype(dtype)
        elif dtype in ['int16', 'uint8']:
            return np.dtype(dtype)
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")

    def read(self, start_sample: int = 0, n_samples: Optional[int] = None) -> np.ndarray:
        bytes_per_element = self.np_dtype.itemsize
        
        is_complex = self.dtype_str in ['complex64', 'complex128']
        
        if is_complex:
            offset = start_sample * bytes_per_element
            count = -1 if n_samples is None else n_samples
            return np.fromfile(self.path, dtype=self.np_dtype, count=count, offset=offset)
        else:
            offset = start_sample * bytes_per_element * 2
            count = -1 if n_samples is None else n_samples * 2
            data = np.fromfile(self.path, dtype=self.np_dtype, count=count, offset=offset)
            # convert to complex
            return data[0::2].astype(np.float32) + 1j * data[1::2].astype(np.float32)

    def num_samples(self) -> int:
        file_size = self.path.stat().st_size
        bytes_per_element = self.np_dtype.itemsize
        is_complex = self.dtype_str in ['complex64', 'complex128']
        
        if is_complex:
            return file_size // bytes_per_element
        else:
            return file_size // (bytes_per_element * 2)

    def file_duration_seconds(self) -> float:
        if self.sample_rate <= 0:
            return 0.0
        return self.num_samples() / self.sample_rate
