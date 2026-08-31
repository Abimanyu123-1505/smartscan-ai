import json

class ReportGenerator:
    @staticmethod
    def generate_markdown(results, path):
        with open(path, "w") as f:
            f.write("# Experiment Report\n\n")
            f.write("## Results\n")
            f.write(json.dumps(results, indent=2))
            
    @staticmethod
    def generate_json(results, path):
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
