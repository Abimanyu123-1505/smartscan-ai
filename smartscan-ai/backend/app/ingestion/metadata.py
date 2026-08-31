from pydantic import BaseModel
from typing import List

class RecordingMetadata(BaseModel):
    sample_rate: float
    center_frequency: float
    duration: float
    datatype: str

class DatasetMetadata(BaseModel):
    name: str
    version: str
    recordings: List[RecordingMetadata]
