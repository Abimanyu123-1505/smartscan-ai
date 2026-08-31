class DatasetLoader:
    def __init__(self):
        self.cache = {}
        
    def load(self, dataset_id):
        if dataset_id in self.cache:
            return self.cache[dataset_id]
        data = [] 
        self.cache[dataset_id] = data
        return data
