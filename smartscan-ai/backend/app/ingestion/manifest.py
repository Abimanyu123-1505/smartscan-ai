import yaml

def parse_manifest(manifest_path: str):
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)
