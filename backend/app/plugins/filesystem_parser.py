"""
Filesystem Parsing (Phase 1 deliverable).

Real digital forensics tools parse raw disk images (E01/AFF4/raw) via
SleuthKit. DFIOP's acquisition layer is built to accept those formats,
but mounting/parsing a real disk image requires native libraries
(libewf, TSK) that aren't available in every deployment target. This
plugin parses the two acquisition types Phase 1 guarantees everywhere:
a mounted directory tree, or a zip/archive bundle of files -- exactly
the shape of evidence exported from a triage tool or collected from a
live endpoint. Swapping in pytsk3 for raw/E01 images is a drop-in
replacement behind the same ParserPlugin interface (see base.py).
"""
import os
import zipfile
import tempfile
import datetime as dt
import hashlib
from typing import List, Dict, Any

from .base import ParserPlugin

CARVE_SIGNATURES = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"%PDF-": "pdf",
    b"PK\x03\x04": "zip_or_docx",
}


def _sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _guess_carved_type(path: str) -> str:
    try:
        with open(path, "rb") as f:
            head = f.read(8)
        for sig, kind in CARVE_SIGNATURES.items():
            if head.startswith(sig):
                return kind
    except OSError:
        pass
    return "unknown"


class FilesystemParser(ParserPlugin):
    name = "filesystem_parser"
    description = (
        "Walks an extracted directory or zip bundle, recording file "
        "metadata (name, size, MAC timestamps, hash) for every entry, "
        "the Phase 1 equivalent of SleuthKit MFT parsing."
    )

    def can_handle(self, path: str) -> bool:
        return os.path.isdir(path) or zipfile.is_zipfile(path)

    def parse(self, path: str) -> List[Dict[str, Any]]:
        if zipfile.is_zipfile(path):
            return self._parse_zip(path)
        if os.path.isdir(path):
            return self._parse_dir(path)
        return []

    def _parse_dir(self, root: str) -> List[Dict[str, Any]]:
        artifacts = []
        for dirpath, _dirnames, filenames in os.walk(root):
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(full)
                except OSError:
                    continue
                artifacts.append(
                    {
                        "artifact_type": "file",
                        "operation": "observed",
                        "name": fname,
                        "path": os.path.relpath(full, root),
                        "size_bytes": stat.st_size,
                        "sha256": _sha256_of(full),
                        "created_ts": dt.datetime.utcfromtimestamp(stat.st_ctime),
                        "modified_ts": dt.datetime.utcfromtimestamp(stat.st_mtime),
                        "accessed_ts": dt.datetime.utcfromtimestamp(stat.st_atime),
                        "extra": {"carved_type": _guess_carved_type(full)},
                    }
                )
        return artifacts

    def _parse_zip(self, zpath: str) -> List[Dict[str, Any]]:
        artifacts = []
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(zpath) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    try:
                        extracted = zf.extract(info, tmp)
                    except Exception:
                        continue
                    mtime = dt.datetime(*info.date_time) if info.date_time else None
                    artifacts.append(
                        {
                            "artifact_type": "file",
                            "operation": "observed",
                            "name": os.path.basename(info.filename),
                            "path": info.filename,
                            "size_bytes": info.file_size,
                            "sha256": _sha256_of(extracted),
                            "created_ts": mtime,
                            "modified_ts": mtime,
                            "accessed_ts": None,
                            "extra": {"carved_type": _guess_carved_type(extracted)},
                        }
                    )
        return artifacts
