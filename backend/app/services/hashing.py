"""Cryptographic verification helpers (Security and Trust Controls).

Every evidence file gets SHA-256, SHA-1, and MD5 computed on acquisition,
and can be re-verified on demand to detect tampering.
"""
import hashlib


def hash_file(path: str, chunk_size: int = 1024 * 1024):
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    size = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
            sha1.update(chunk)
            md5.update(chunk)
            size += len(chunk)
    return {
        "sha256": sha256.hexdigest(),
        "sha1": sha1.hexdigest(),
        "md5": md5.hexdigest(),
        "size_bytes": size,
    }
