from .cleaning import remove_dc
from .normalization import power_normalize

class PreprocessingPipeline:
    def __init__(self):
        self.steps = [remove_dc, power_normalize]
        
    def process(self, data):
        for step in self.steps:
            data = step(data)
        return data
