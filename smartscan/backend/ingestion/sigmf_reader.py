"""
smartcan.backend.ingestion.sigmf_reader
=======================================
Parses SigMF recordings (.sigmf-meta + .sigmf-data).

SigMF spec: https://github.com/sigmf/SigMF

This reader is the PRIMARY interface between real RF recordings and the
SmartScan replay engine. It MUST NOT synthesize or modify the signal.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import numpy as np

from .metadata import RecordingMetadata, ValidationResult, validate_sigmf_meta

logger = logging.getLogger(__name__)

class SigMFReader:
    def __init__(self, meta_path: Union[str, Path], data_path: Optional[Union[str, Path]] = None):
        """Initialize the SigMF reader with a meta file path and optional data file path."""
        self.meta_path = Path(meta_path)
        if not self.meta_path.exists():
            raise FileNotFoundError(f"SigMF meta file not found: {self.meta_path}")
            
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = self.meta_path.with_suffix('.sigmf-data')
            
        self.meta_dict = self._load_meta()

    def _load_meta(self) -> dict:
        """Reads JSON .sigmf-meta file."""
        with open(self.meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate(self) -> ValidationResult:
        """Validates required fields in the SigMF metadata."""
        return validate_sigmf_meta(self.meta_dict)

    def get_metadata(self) -> RecordingMetadata:
        """Parses the loaded dictionary into a RecordingMetadata object."""
        global_meta = self.meta_dict.get('global', {})
        captures = self.meta_dict.get('captures', [])
        
        # Simple extraction
        datatype = global_meta.get('core:datatype', 'cf32_le')
        sample_rate = global_meta.get('core:sample_rate', 1.0)
        center_freq = captures[0].get('core:frequency', 0.0) if captures else 0.0
        start_time = captures[0].get('core:datetime') if captures else None
        
        hw = global_meta.get('core:hw', '')
        desc = global_meta.get('core:description', '')
        
        num_samples = 0
        if self.data_path.exists():
            file_size = self.data_path.stat().st_size
            if datatype in ['cf32_le', 'cf32']:
                num_samples = file_size // 8
            elif datatype in ['cf64_le', 'cf64']:
                num_samples = file_size // 16
            elif datatype in ['ci16_le', 'ci16']:
                num_samples = file_size // 4
            elif datatype in ['ri16_le', 'ri16']:
                num_samples = file_size // 2

        return RecordingMetadata(
            recording_id=self.meta_path.stem,
            dataset_id="unknown_dataset",
            filename=self.meta_path.name,
            center_frequency_hz=center_freq,
            sample_rate_hz=sample_rate,
            bandwidth_hz=sample_rate,
            num_samples=num_samples,
            start_time=start_time,
            hardware=hw,
            datatype=datatype,
            capture_segments=self.get_capture_segments(),
            annotations=self.get_annotations()
        )

    def read_samples(self, start_idx: int = 0, num_samples: Optional[int] = None) -> np.ndarray:
        """Reads complex IQ from .sigmf-data."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"SigMF data file not found: {self.data_path}")
            
        datatype = self.meta_dict.get('global', {}).get('core:datatype', 'cf32_le')
        
        dtype_map = {
            'cf32_le': np.complex64,
            'cf32': np.complex64,
            'cf64_le': np.complex128,
            'cf64': np.complex128,
            'ci16_le': np.int16,
            'ci16': np.int16,
            'ri16_le': np.int16,
            'ri16': np.int16
        }
        
        if datatype not in dtype_map:
            raise ValueError(f"Unsupported datatype: {datatype}")
            
        np_dtype = dtype_map[datatype]
        
        bytes_per_sample = np.dtype(np_dtype).itemsize
        if datatype.startswith('c'):
            # Complex types might just read as complex arrays
            pass
            
        offset = start_idx * bytes_per_sample
        if datatype.startswith('c'):
             offset = start_idx * np.dtype(np_dtype).itemsize
        else:
             offset = start_idx * np.dtype(np_dtype).itemsize * 2
             
        count = -1
        if num_samples is not None:
             count = num_samples if datatype.startswith('c') else num_samples * 2
             
        data = np.fromfile(self.data_path, dtype=np_dtype, count=count, offset=offset)
        
        if datatype.startswith('c'):
            return data
        else:
            # Need to form complex from real and imag interleaved
            return data[0::2] + 1j * data[1::2]

    def get_capture_segments(self) -> List[Dict[str, Any]]:
        """Returns all capture segments with timestamps and frequencies."""
        return self.meta_dict.get('captures', [])

    def get_annotations(self) -> List[Dict[str, Any]]:
        """Returns all annotation entries."""
        return self.meta_dict.get('annotations', [])

    def summary(self) -> dict:
        """Human-readable summary."""
        meta = self.get_metadata()
        return {
            "recording_id": meta.recording_id,
            "center_freq_mhz": meta.center_frequency_hz / 1e6,
            "sample_rate_mhz": meta.sample_rate_hz / 1e6,
            "duration_s": meta.num_samples / meta.sample_rate_hz if meta.sample_rate_hz else 0,
            "datatype": meta.datatype,
            "annotations_count": len(meta.annotations)
        }
