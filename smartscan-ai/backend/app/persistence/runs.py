import json
import os

class RunLogger:
    def __init__(self, log_dir="logs/runs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
    def log(self, run_id, data):
        path = os.path.join(self.log_dir, f"{run_id}.json")
        with open(path, "w") as f:
            json.dump(data, f)
