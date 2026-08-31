"""
Core data model for DFIOP — Phase 2 / Enterprise Rebuild.

Covers all modules: Case Management, Evidence Acquisition, Artifacts,
Timeline, Search, RBAC, IOC, YARA, Sigma, MITRE ATT&CK, Memory
Forensics, Disk Forensics, Network Forensics, Registry Analysis,
Malware Analysis, Graph Entities, Chain of Custody, and AI sessions.
"""
import json
import uuid
import datetime as dt
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base


def new_id() -> str:
    return uuid.uuid4().hex[:12]


# ===========================================================================
# RBAC
# ===========================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=new_id)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, default="")
    role = Column(String, default="investigator")  # administrator|investigator|reviewer|auditor|guest
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    avatar_initials = Column(String, default="")


# ===========================================================================
# Case Management
# ===========================================================================

class Case(Base):
    __tablename__ = "cases"
    id = Column(String, primary_key=True, default=new_id)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    investigator = Column(String, default="")
    status = Column(String, default="open")          # open|active|closed|archived
    priority = Column(String, default="medium")       # low|medium|high|critical
    incident_type = Column(String, default="")        # malware|data_breach|insider|phishing|ransomware|other
    organization = Column(String, default="")
    reference_number = Column(String, default="")
    tags_json = Column(Text, default="[]")
    notes = Column(Text, default="")
    risk_score = Column(Float, default=0.0)           # 0–100, computed
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")

    @property
    def tags(self):
        return json.loads(self.tags_json or "[]")


# ===========================================================================
# Evidence Acquisition
# ===========================================================================

class Evidence(Base):
    """A single acquired item. Original bytes stored read-only, hashed at acquisition."""
    __tablename__ = "evidence"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    evidence_type = Column(String, default="filesystem_bundle")
    # filesystem_bundle|raw_image|e01|memory_dump|pcap|registry_hive|browser_profile|single_file
    size_bytes = Column(Integer, default=0)
    sha256 = Column(String, nullable=False)
    sha1 = Column(String, nullable=False)
    md5 = Column(String, nullable=False)
    acquired_at = Column(DateTime, default=dt.datetime.utcnow)
    acquired_by = Column(String, default="")
    verified_at = Column(DateTime, nullable=True)
    verification_ok = Column(String, default="unverified")  # unverified|ok|mismatch
    description = Column(Text, default="")
    source_device = Column(String, default="")

    case = relationship("Case", back_populates="evidence_items")
    artifacts = relationship("Artifact", back_populates="evidence", cascade="all, delete-orphan")


# ===========================================================================
# Artifacts (unified schema — filesystem, browser, memory, network, registry)
# ===========================================================================

class Artifact(Base):
    """Parsed evidence item. All forensic sources produce Artifacts."""
    __tablename__ = "artifacts"
    id = Column(String, primary_key=True, default=new_id)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    case_id = Column(String, nullable=False)
    artifact_type = Column(String, nullable=False)
    # file|deleted_file|browser_history|browser_cookie|browser_download|
    # registry_key|process|network_connection|memory_region|event_log|
    # yara_match|ioc_hit|malware_sample
    operation = Column(String, default="")
    name = Column(String, default="")
    path = Column(String, default="")
    size_bytes = Column(Integer, default=0)
    sha256 = Column(String, default="")
    created_ts = Column(DateTime, nullable=True)
    modified_ts = Column(DateTime, nullable=True)
    accessed_ts = Column(DateTime, nullable=True)
    user = Column(String, default="")
    process = Column(String, default="")
    extra_json = Column(Text, default="{}")
    parser_plugin = Column(String, default="")
    flagged_score = Column(Float, default=0.0)
    flagged_reason = Column(Text, default="")
    labels_json = Column(Text, default="[]")
    confidence = Column(Float, default=1.0)
    source_refs_json = Column(Text, default="[]")
    bookmarked = Column(Boolean, default=False)
    bookmark_note = Column(Text, default="")

    evidence = relationship("Evidence", back_populates="artifacts")

    @property
    def labels(self):
        return json.loads(self.labels_json or "[]")

    @property
    def source_refs(self):
        return json.loads(self.source_refs_json or "[]")

    @property
    def extra(self):
        return json.loads(self.extra_json or "{}")


# ===========================================================================
# Timeline
# ===========================================================================

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    artifact_id = Column(String, ForeignKey("artifacts.id"), nullable=False)
    event_ts = Column(DateTime, nullable=False)
    event_type = Column(String, default="")    # created|modified|accessed|visited|executed|connected
    summary = Column(String, default="")
    source_type = Column(String, default="")   # filesystem|browser|memory|network|registry|event_log
    severity = Column(String, default="info")  # info|low|medium|high|critical
    mitre_technique = Column(String, default="")


# ===========================================================================
# Chain of Custody
# ===========================================================================

class AuditLog(Base):
    """Append-only, hash-chained chain-of-custody log."""
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    actor = Column(String, default="analyst")
    action = Column(String, nullable=False)
    detail = Column(Text, default="")
    timestamp = Column(DateTime, default=dt.datetime.utcnow)
    ip_address = Column(String, default="")
    prev_hash = Column(String, default="")
    entry_hash = Column(String, default="")

    case = relationship("Case", back_populates="audit_logs")


# ===========================================================================
# IOC Hunting
# ===========================================================================

class IOC(Base):
    __tablename__ = "iocs"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    ioc_type = Column(String, nullable=False)  # hash|domain|ip|email|url|filename
    value = Column(String, nullable=False)
    description = Column(Text, default="")
    source = Column(String, default="analyst")  # analyst|virustotal|misp|auto
    risk_score = Column(Float, default=0.0)
    tags_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    confirmed = Column(Boolean, default=False)


class IOCMatch(Base):
    __tablename__ = "ioc_matches"
    id = Column(String, primary_key=True, default=new_id)
    ioc_id = Column(String, ForeignKey("iocs.id"), nullable=False)
    artifact_id = Column(String, ForeignKey("artifacts.id"), nullable=False)
    case_id = Column(String, nullable=False)
    match_context = Column(Text, default="")
    matched_at = Column(DateTime, default=dt.datetime.utcnow)


# ===========================================================================
# YARA
# ===========================================================================

class YARARule(Base):
    __tablename__ = "yara_rules"
    id = Column(String, primary_key=True, default=new_id)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    rule_text = Column(Text, nullable=False)
    author = Column(String, default="")
    tags_json = Column(Text, default="[]")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    match_count = Column(Integer, default=0)


class YARAMatch(Base):
    __tablename__ = "yara_matches"
    id = Column(String, primary_key=True, default=new_id)
    rule_id = Column(String, ForeignKey("yara_rules.id"), nullable=False)
    case_id = Column(String, nullable=False)
    artifact_id = Column(String, ForeignKey("artifacts.id"), nullable=True)
    file_path = Column(String, default="")
    matched_strings_json = Column(Text, default="[]")  # [{name, offset, data}]
    matched_at = Column(DateTime, default=dt.datetime.utcnow)


# ===========================================================================
# Sigma
# ===========================================================================

class SigmaRule(Base):
    __tablename__ = "sigma_rules"
    id = Column(String, primary_key=True, default=new_id)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    rule_yaml = Column(Text, nullable=False)
    severity = Column(String, default="medium")  # low|medium|high|critical
    mitre_technique = Column(String, default="")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class SigmaAlert(Base):
    __tablename__ = "sigma_alerts"
    id = Column(String, primary_key=True, default=new_id)
    rule_id = Column(String, ForeignKey("sigma_rules.id"), nullable=False)
    case_id = Column(String, nullable=False)
    severity = Column(String, default="medium")
    title = Column(String, default="")
    description = Column(Text, default="")
    event_data_json = Column(Text, default="{}")
    mitre_technique = Column(String, default="")
    detected_at = Column(DateTime, default=dt.datetime.utcnow)
    acknowledged = Column(Boolean, default=False)


# ===========================================================================
# MITRE ATT&CK
# ===========================================================================

class MITREMapping(Base):
    __tablename__ = "mitre_mappings"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    artifact_id = Column(String, ForeignKey("artifacts.id"), nullable=True)
    technique_id = Column(String, nullable=False)   # T1059, T1078, etc.
    technique_name = Column(String, default="")
    tactic = Column(String, default="")             # execution|persistence|etc.
    sub_technique = Column(String, default="")
    confidence = Column(Float, default=0.5)
    source = Column(String, default="auto")         # auto|sigma|yara|analyst
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


# ===========================================================================
# Memory Forensics
# ===========================================================================

class MemoryArtifact(Base):
    __tablename__ = "memory_artifacts"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    artifact_type = Column(String, nullable=False)  # process|dll|handle|connection|driver|registry_hive
    pid = Column(Integer, nullable=True)
    ppid = Column(Integer, nullable=True)
    name = Column(String, default="")
    path = Column(String, default="")
    command_line = Column(Text, default="")
    start_time = Column(DateTime, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    base_address = Column(String, default="")
    size = Column(Integer, default=0)
    suspicious = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)
    injected = Column(Boolean, default=False)
    extra_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


# ===========================================================================
# Network Forensics
# ===========================================================================

class NetworkArtifact(Base):
    __tablename__ = "network_artifacts"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    protocol = Column(String, default="")           # TCP|UDP|DNS|HTTP|TLS|SMB|FTP|SSH|SMTP
    src_ip = Column(String, default="")
    src_port = Column(Integer, nullable=True)
    dst_ip = Column(String, default="")
    dst_port = Column(Integer, nullable=True)
    hostname = Column(String, default="")
    url = Column(Text, default="")
    method = Column(String, default="")
    status_code = Column(Integer, nullable=True)
    bytes_sent = Column(Integer, default=0)
    bytes_recv = Column(Integer, default=0)
    tls_sni = Column(String, default="")
    dns_query = Column(String, default="")
    dns_response = Column(String, default="")
    timestamp = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, default=0)
    flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, default="")
    extra_json = Column(Text, default="{}")


# ===========================================================================
# Registry Analysis
# ===========================================================================

class RegistryKey(Base):
    __tablename__ = "registry_keys"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    hive = Column(String, default="")              # SYSTEM|SOFTWARE|SAM|SECURITY|NTUSER.DAT
    key_path = Column(Text, nullable=False)
    value_name = Column(String, default="")
    value_type = Column(String, default="")        # REG_SZ|REG_DWORD|REG_BINARY|etc.
    value_data = Column(Text, default="")
    last_modified = Column(DateTime, nullable=True)
    category = Column(String, default="")          # run_key|usb|mru|shellbag|installed_app|network|user
    flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, default="")
    extra_json = Column(Text, default="{}")


# ===========================================================================
# Malware Analysis
# ===========================================================================

class MalwareSample(Base):
    __tablename__ = "malware_samples"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    artifact_id = Column(String, ForeignKey("artifacts.id"), nullable=True)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True)
    sha256 = Column(String, nullable=False)
    sha1 = Column(String, default="")
    md5 = Column(String, default="")
    filename = Column(String, default="")
    file_type = Column(String, default="")         # PE32|PE64|ELF|Mach-O|Script|Document
    arch = Column(String, default="")
    file_size = Column(Integer, default=0)
    entropy = Column(Float, default=0.0)
    is_packed = Column(Boolean, default=False)
    packer_name = Column(String, default="")
    is_signed = Column(Boolean, default=False)
    signature_valid = Column(Boolean, nullable=True)
    imphash = Column(String, default="")
    sections_json = Column(Text, default="[]")     # [{name, vsize, rsize, entropy, md5}]
    imports_json = Column(Text, default="[]")      # [{dll, functions:[]}]
    exports_json = Column(Text, default="[]")
    strings_json = Column(Text, default="[]")      # extracted strings
    suspicious_apis_json = Column(Text, default="[]")
    mitre_techniques_json = Column(Text, default="[]")
    risk_score = Column(Float, default=0.0)
    analyzed_at = Column(DateTime, default=dt.datetime.utcnow)
    analysis_status = Column(String, default="pending")  # pending|complete|error


# ===========================================================================
# Graph Entities
# ===========================================================================

class GraphNode(Base):
    __tablename__ = "graph_nodes"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    node_type = Column(String, nullable=False)   # file|process|user|ip|domain|registry|email
    label = Column(String, default="")
    properties_json = Column(Text, default="{}")
    risk_score = Column(Float, default=0.0)
    artifact_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class GraphEdge(Base):
    __tablename__ = "graph_edges"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    source_node_id = Column(String, ForeignKey("graph_nodes.id"), nullable=False)
    target_node_id = Column(String, ForeignKey("graph_nodes.id"), nullable=False)
    edge_type = Column(String, nullable=False)   # communicates_with|downloaded|executed|wrote|reads|spawned
    label = Column(String, default="")
    weight = Column(Float, default=1.0)
    properties_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


# ===========================================================================
# AI Sessions
# ===========================================================================

class AISession(Base):
    __tablename__ = "ai_sessions"
    id = Column(String, primary_key=True, default=new_id)
    case_id = Column(String, nullable=False)
    user = Column(String, default="analyst")
    messages_json = Column(Text, default="[]")  # [{role, content, citations, ts}]
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)
