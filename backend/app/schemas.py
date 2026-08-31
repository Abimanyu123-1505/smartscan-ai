import datetime as dt
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict


# ─── Auth ────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ""
    role: str = "investigator"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: dt.datetime
    last_login: Optional[dt.datetime]
    avatar_initials: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class LoginRequest(BaseModel):
    username: str
    password: str


# ─── Cases ───────────────────────────────────────────────────────────────────
class CaseCreate(BaseModel):
    name: str
    description: str = ""
    investigator: str = ""
    priority: str = "medium"
    incident_type: str = ""
    organization: str = ""
    reference_number: str = ""
    tags: List[str] = []
    notes: str = ""

class CaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    investigator: str
    status: str
    priority: str
    incident_type: str
    organization: str
    reference_number: str
    tags: List[str] = []
    notes: str
    risk_score: float
    created_at: dt.datetime
    updated_at: dt.datetime
    closed_at: Optional[dt.datetime]


# ─── Evidence ────────────────────────────────────────────────────────────────
class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    original_filename: str
    evidence_type: str
    size_bytes: int
    sha256: str
    sha1: str
    md5: str
    acquired_at: dt.datetime
    acquired_by: str
    verification_ok: str
    description: str
    source_device: str


# ─── Artifacts ───────────────────────────────────────────────────────────────
class ArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    evidence_id: str
    artifact_type: str
    operation: str
    name: str
    path: str
    size_bytes: int
    sha256: str
    created_ts: Optional[dt.datetime]
    modified_ts: Optional[dt.datetime]
    accessed_ts: Optional[dt.datetime]
    user: str
    process: str
    parser_plugin: str
    flagged_score: float
    flagged_reason: str
    labels: List[str] = []
    confidence: float
    source_refs: List[dict] = []
    bookmarked: bool
    bookmark_note: str

class LabelUpdate(BaseModel):
    label: str
    verified_by: Optional[str] = None


# ─── Timeline ────────────────────────────────────────────────────────────────
class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    artifact_id: str
    event_ts: dt.datetime
    event_type: str
    summary: str
    source_type: str
    severity: str
    mitre_technique: str


# ─── Audit / Chain of Custody ────────────────────────────────────────────────
class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    actor: str
    action: str
    detail: str
    timestamp: dt.datetime
    ip_address: str
    prev_hash: str
    entry_hash: str


# ─── Search ──────────────────────────────────────────────────────────────────
class SearchResult(BaseModel):
    artifact_id: str
    case_id: str
    artifact_type: str
    name: str
    path: str
    snippet: str


# ─── Dashboard ───────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    open_cases: int
    closed_cases: int
    total_evidence: int
    total_artifacts: int
    timeline_events: int
    malware_found: int
    high_risk_cases: int
    storage_used_mb: float
    ioc_hits: int
    yara_matches: int
    sigma_alerts: int


# ─── IOC ─────────────────────────────────────────────────────────────────────
class IOCCreate(BaseModel):
    ioc_type: str
    value: str
    description: str = ""
    source: str = "analyst"
    risk_score: float = 0.0
    tags: List[str] = []

class IOCOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    ioc_type: str
    value: str
    description: str
    source: str
    risk_score: float
    created_at: dt.datetime
    confirmed: bool

class IOCMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    ioc_id: str
    artifact_id: str
    case_id: str
    match_context: str
    matched_at: dt.datetime


# ─── YARA ────────────────────────────────────────────────────────────────────
class YARARuleCreate(BaseModel):
    name: str
    description: str = ""
    rule_text: str
    author: str = ""
    tags: List[str] = []

class YARARuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    author: str
    enabled: bool
    created_at: dt.datetime
    match_count: int
    rule_text: str

class YARAMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    rule_id: str
    case_id: str
    file_path: str
    matched_at: dt.datetime


# ─── Sigma ───────────────────────────────────────────────────────────────────
class SigmaRuleCreate(BaseModel):
    name: str
    description: str = ""
    rule_yaml: str
    severity: str = "medium"
    mitre_technique: str = ""

class SigmaRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    severity: str
    mitre_technique: str
    enabled: bool
    created_at: dt.datetime

class SigmaAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    rule_id: str
    case_id: str
    severity: str
    title: str
    description: str
    mitre_technique: str
    detected_at: dt.datetime
    acknowledged: bool


# ─── MITRE ───────────────────────────────────────────────────────────────────
class MITREMappingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    technique_id: str
    technique_name: str
    tactic: str
    sub_technique: str
    confidence: float
    source: str
    notes: str
    created_at: dt.datetime


# ─── Memory ──────────────────────────────────────────────────────────────────
class MemoryArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    artifact_type: str
    pid: Optional[int]
    ppid: Optional[int]
    name: str
    path: str
    command_line: str
    start_time: Optional[dt.datetime]
    suspicious: bool
    hidden: bool
    injected: bool


# ─── Network ─────────────────────────────────────────────────────────────────
class NetworkArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    protocol: str
    src_ip: str
    src_port: Optional[int]
    dst_ip: str
    dst_port: Optional[int]
    hostname: str
    url: str
    bytes_sent: int
    bytes_recv: int
    tls_sni: str
    dns_query: str
    timestamp: Optional[dt.datetime]
    flagged: bool
    flag_reason: str


# ─── Registry ────────────────────────────────────────────────────────────────
class RegistryKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    hive: str
    key_path: str
    value_name: str
    value_type: str
    value_data: str
    last_modified: Optional[dt.datetime]
    category: str
    flagged: bool
    flag_reason: str


# ─── Malware ─────────────────────────────────────────────────────────────────
class MalwareSampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    sha256: str
    sha1: str
    md5: str
    filename: str
    file_type: str
    arch: str
    file_size: int
    entropy: float
    is_packed: bool
    packer_name: str
    is_signed: bool
    risk_score: float
    analyzed_at: dt.datetime
    analysis_status: str


# ─── Graph ───────────────────────────────────────────────────────────────────
class GraphNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    node_type: str
    label: str
    risk_score: float
    artifact_id: Optional[str]

class GraphEdgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    label: str
    weight: float


# ─── AI ──────────────────────────────────────────────────────────────────────
class AIMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class AIMessageOut(BaseModel):
    session_id: str
    role: str
    content: str
    citations: List[Dict[str, Any]] = []
    timestamp: dt.datetime
