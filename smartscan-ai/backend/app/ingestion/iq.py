import numpy as np

class IQReader:
    def __init__(self, file_path: str, dtype=np.complex64):
        self.file_path = file_path
        self.dtype = dtype

    def read(self):
        return np.fromfile(self.file_path, dtype=self.dtype)
