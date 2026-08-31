"""
Plugin/SDK Framework (Phase 1: core support, Phase 2+: full parser API).

A parser plugin takes a filesystem path (already acquired, read-only,
hashed) and yields standardized artifact dicts. This is the seam the
roadmap describes: "input JSON events, output graph nodes/events" -- new
artifact sources (registry hives, PCAPs, cloud logs, mobile backups) are
added by writing a new plugin, not by touching the core engine.

To add a plugin:
  1. Subclass ParserPlugin.
  2. Implement `can_handle(path)` -> bool and `parse(path)` -> list[dict].
  3. Register an instance in app/plugins/__init__.py's PLUGIN_REGISTRY.

Each artifact dict may contain:
    artifact_type, name, path, size_bytes, sha256,
    created_ts, modified_ts, accessed_ts, extra: dict
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ParserPlugin(ABC):
    name: str = "unnamed_plugin"
    description: str = ""

    @abstractmethod
    def can_handle(self, path: str) -> bool:
        ...

    @abstractmethod
    def parse(self, path: str) -> List[Dict[str, Any]]:
        ...
