class ExperimentRunner:
    def __init__(self, config):
        self.config = config
        
    def run(self):
        print(f"Running experiment with config {self.config}")
        return {"status": "success"}
