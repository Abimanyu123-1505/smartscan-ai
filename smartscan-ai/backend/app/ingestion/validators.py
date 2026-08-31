from ..core.exceptions import MetadataError

def validate_sigmf(meta: dict):
    if 'global' not in meta or 'core:sample_rate' not in meta['global']:
        raise MetadataError("Missing global core:sample_rate in SigMF meta")
    if 'captures' not in meta or not meta['captures']:
        raise MetadataError("Missing captures in SigMF meta")
    return True
