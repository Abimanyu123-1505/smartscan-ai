import json
import numpy as np
from pathlib import Path

class SigMFReader:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.meta_path = file_path.with_suffix('.sigmf-meta')
        self.data_path = file_path.with_suffix('.sigmf-data')
    
    def read_meta(self):
        with open(self.meta_path, 'r') as f:
            return json.load(f)
            
    def read_data(self, dtype=np.complex64):
        return np.fromfile(self.data_path, dtype=dtype)
