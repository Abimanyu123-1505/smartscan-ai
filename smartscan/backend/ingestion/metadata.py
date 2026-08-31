from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any

class DatasetMetadata(BaseModel):
    dataset_id: str
    name: str
    source: str
    doi: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None
    measurement_type: str
    frequency_range_hz: Tuple[float, float]
    sample_rate_hz: float
    duration_seconds: float
    location: Optional[str] = None
    format: str
    metadata_available: bool
    labels_available: bool
    notes: Optional[str] = None
    limitations: Optional[str] = None

class RecordingMetadata(BaseModel):
    recording_id: str
    dataset_id: str
    filename: str
    center_frequency_hz: float
    sample_rate_hz: float
    bandwidth_hz: float
    num_samples: int
    start_time: Optional[str] = None
    hardware: Optional[str] = None
    location: Optional[str] = None
    antenna: Optional[str] = None
    datatype: str
    capture_segments: List[Dict[str, Any]] = Field(default_factory=list)
    annotations: List[Dict[str, Any]] = Field(default_factory=list)

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

def validate_sigmf_meta(meta_dict: dict) -> ValidationResult:
    errors = []
    warnings = []
    
    global_meta = meta_dict.get('global', {})
    if 'core:datatype' not in global_meta:
        errors.append("Missing required field: global.core:datatype")
    if 'core:sample_rate' not in global_meta:
        errors.append("Missing required field: global.core:sample_rate")
        
    captures = meta_dict.get('captures', [])
    if not isinstance(captures, list) or not captures:
        errors.append("Missing or empty required field: captures")
    else:
        for i, cap in enumerate(captures):
            if 'core:frequency' not in cap:
                errors.append(f"Capture {i} missing required field: core:frequency")
                
    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
