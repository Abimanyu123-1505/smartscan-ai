import os

class ArtifactSaver:
    def __init__(self, art_dir="logs/artifacts"):
        self.art_dir = art_dir
        os.makedirs(self.art_dir, exist_ok=True)
        
    def save_plot(self, fig, name):
        fig.savefig(os.path.join(self.art_dir, f"{name}.png"))
