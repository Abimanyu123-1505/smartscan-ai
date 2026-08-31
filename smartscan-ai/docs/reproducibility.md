# Reproducibility

Reproducibility is paramount.
- All environment variables are fixed (e.g., `SEED=42`).
- Python library versions are pinned in `pyproject.toml`.
- Dataset hashes are documented and verified before each major training run.
- Docker containers guarantee uniform execution environments.
