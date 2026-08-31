import os

class CheckpointManager:
    def __init__(self, ckpt_dir="logs/checkpoints"):
        self.ckpt_dir = ckpt_dir
        os.makedirs(self.ckpt_dir, exist_ok=True)
        
    def save(self, model, name):
        pass # Model specific save
        
    def load(self, name):
        pass # Model specific load
