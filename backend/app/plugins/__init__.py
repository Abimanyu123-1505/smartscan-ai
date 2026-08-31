"""
Plugin registry. Phase 1 ships two working parsers. The stub classes
below aren't wired into acquisition yet -- they document the exact
extension point each Phase 2/3 roadmap module will use, per the Plugin
and SDK Strategy section, so the interface doesn't change shape later.
"""
from typing import List
from .base import ParserPlugin
from .filesystem_parser import FilesystemParser
from .browser_history_parser import BrowserHistoryParser

# Active Phase 1 plugins, tried in order against each acquired item.
PLUGIN_REGISTRY: List[ParserPlugin] = [
    BrowserHistoryParser(),
    FilesystemParser(),
]


class MemoryForensicsPlugin(ParserPlugin):
    """Phase 2 stub. Will wrap Volatility3 to extract processes, loaded
    modules, and network sockets from a memory dump. Not registered yet."""

    name = "memory_forensics_plugin"
    description = "Volatility3-backed memory dump parser (Phase 2, not implemented)."

    def can_handle(self, path: str) -> bool:
        return path.endswith((".mem", ".raw", ".vmem", ".dmp"))

    def parse(self, path: str):
        raise NotImplementedError(
            "Phase 2: integrate Volatility3 (pip install volatility3) and "
            "map its process/network plugins to artifact_type='process' "
            "and artifact_type='network_connection'."
        )


class NetworkPcapPlugin(ParserPlugin):
    """Phase 2 stub. Will use scapy/dpkt to parse PCAP/PCAPNG into
    per-flow artifacts (DNS, HTTP, TLS SNI, SMB)."""

    name = "network_pcap_plugin"
    description = "PCAP/PCAPNG flow parser (Phase 2, not implemented)."

    def can_handle(self, path: str) -> bool:
        return path.endswith((".pcap", ".pcapng"))

    def parse(self, path: str):
        raise NotImplementedError(
            "Phase 2: integrate scapy or dpkt, aggregate packets into "
            "flows, and emit artifact_type='network_flow' with "
            "extra={'src_ip','dst_ip','protocol','sni'}."
        )


class WindowsRegistryPlugin(ParserPlugin):
    """Phase 2 stub. Will parse registry hives (SYSTEM/SAM/NTUSER.DAT)
    via python-registry or similar for ShimCache, Shellbags, USB history."""

    name = "windows_registry_plugin"
    description = "Registry hive parser (Phase 2, not implemented)."

    def can_handle(self, path: str) -> bool:
        return path.upper().endswith((".DAT", "NTUSER.DAT", "SYSTEM", "SAM"))

    def parse(self, path: str):
        raise NotImplementedError(
            "Phase 2: integrate python-registry, emit artifact_type in "
            "{'registry_key','usb_device','shellbag','shimcache_entry'}."
        )


class CloudLogPlugin(ParserPlugin):
    """Phase 3 stub. Will ingest AWS CloudTrail / Azure Monitor JSON
    exports into artifact_type='cloud_event'."""

    name = "cloud_log_plugin"
    description = "Cloud audit log ingester (Phase 3, not implemented)."

    def can_handle(self, path: str) -> bool:
        return path.endswith(".json") and "cloudtrail" in path.lower()

    def parse(self, path: str):
        raise NotImplementedError(
            "Phase 3: parse CloudTrail/Azure Monitor JSON records into "
            "artifact_type='cloud_event' with actor/IAM/resource fields."
        )
