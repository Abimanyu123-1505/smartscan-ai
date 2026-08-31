import hashlib

def generate_signature(file_path: str):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def verify_signature(file_path: str, expected_sig: str):
    return generate_signature(file_path) == expected_sig
