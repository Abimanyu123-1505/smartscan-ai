import yaml

class DatasetRegistry:
    def __init__(self, registry_file: str):
        self.registry_file = registry_file
        self.datasets = {}
        
    def load(self):
        with open(self.registry_file, 'r') as f:
            self.datasets = yaml.safe_load(f)
