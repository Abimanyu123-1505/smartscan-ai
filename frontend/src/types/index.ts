// All TypeScript interfaces for DFIOP

export interface Case {
  id: string;
  name: string;
  description: string;
  investigator: string;
  status: "open" | "active" | "closed" | "archived";
  priority: "low" | "medium" | "high" | "critical";
  incident_type: string;
  organization: string;
  reference_number: string;
  tags: string[];
  notes: string;
  risk_score: number;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
}

export interface Evidence {
  id: string;
  case_id: string;
  original_filename: string;
  evidence_type: string;
  size_bytes: number;
  sha256: string;
  sha1: string;
  md5: string;
  acquired_at: string;
  acquired_by: string;
  verification_ok: "unverified" | "ok" | "mismatch";
  description: string;
  source_device: string;
}

export interface Artifact {
  id: string;
  evidence_id: string;
  artifact_type: string;
  operation: string;
  name: string;
  path: string;
  size_bytes: number;
  sha256: string;
  created_ts: string | null;
  modified_ts: string | null;
  accessed_ts: string | null;
  user: string;
  process: string;
  parser_plugin: string;
  flagged_score: number;
  flagged_reason: string;
  labels: string[];
  confidence: number;
  source_refs: Array<{ type: string; artifact_id: string; path?: string; value?: string }>;
  bookmarked: boolean;
  bookmark_note: string;
}

export interface TimelineEvent {
  id: string;
  artifact_id: string;
  event_ts: string;
  event_type: string;
  summary: string;
  source_type: string;
  severity: string;
  mitre_technique: string;
}

export interface AuditLog {
  id: string;
  actor: string;
  action: string;
  detail: string;
  timestamp: string;
  ip_address: string;
  prev_hash: string;
  entry_hash: string;
}

export interface SearchResult {
  artifact_id: string;
  case_id: string;
  artifact_type: string;
  name: string;
  path: string;
  snippet: string;
}

export interface DashboardStats {
  open_cases: number;
  closed_cases: number;
  total_evidence: number;
  total_artifacts: number;
  timeline_events: number;
  malware_found: number;
  high_risk_cases: number;
  storage_used_mb: number;
  ioc_hits: number;
  yara_matches: number;
  sigma_alerts: number;
}

export interface IOC {
  id: string;
  case_id: string;
  ioc_type: string;
  value: string;
  description: string;
  source: string;
  risk_score: number;
  created_at: string;
  confirmed: boolean;
}

export interface IOCMatch {
  id: string;
  ioc_id: string;
  artifact_id: string;
  case_id: string;
  match_context: string;
  matched_at: string;
}

export interface YARARule {
  id: string;
  name: string;
  description: string;
  author: string;
  enabled: boolean;
  created_at: string;
  match_count: number;
  rule_text: string;
}

export interface YARAMatch {
  id: string;
  rule_id: string;
  case_id: string;
  file_path: string;
  matched_at: string;
}

export interface SigmaRule {
  id: string;
  name: string;
  description: string;
  severity: string;
  mitre_technique: string;
  enabled: boolean;
  created_at: string;
}

export interface SigmaRuleCreate {
  name: string;
  description?: string;
  rule_yaml: string;
  severity?: string;
  mitre_technique?: string;
}

export interface SigmaAlert {
  id: string;
  rule_id: string;
  case_id: string;
  severity: string;
  title: string;
  description: string;
  mitre_technique: string;
  detected_at: string;
  acknowledged: boolean;
}

export interface MITRETechnique {
  id: string;
  name: string;
  sub: string[];
}

export interface MITRETactic {
  id: string;
  name: string;
  techniques: MITRETechnique[];
}

export interface MITREMapping {
  id: string;
  case_id: string;
  technique_id: string;
  technique_name: string;
  tactic: string;
  sub_technique: string;
  confidence: number;
  source: string;
  notes: string;
  created_at: string;
}

export interface MemoryArtifact {
  id: string;
  case_id: string;
  artifact_type: string;
  pid: number | null;
  ppid: number | null;
  name: string;
  path: string;
  command_line: string;
  start_time: string | null;
  suspicious: boolean;
  hidden: boolean;
  injected: boolean;
}

export interface NetworkArtifact {
  id: string;
  case_id: string;
  protocol: string;
  src_ip: string;
  src_port: number | null;
  dst_ip: string;
  dst_port: number | null;
  hostname: string;
  url: string;
  bytes_sent: number;
  bytes_recv: number;
  tls_sni: string;
  dns_query: string;
  timestamp: string | null;
  flagged: boolean;
  flag_reason: string;
}

export interface RegistryKey {
  id: string;
  case_id: string;
  hive: string;
  key_path: string;
  value_name: string;
  value_type: string;
  value_data: string;
  last_modified: string | null;
  category: string;
  flagged: boolean;
  flag_reason: string;
}

export interface MalwareSample {
  id: string;
  case_id: string;
  sha256: string;
  sha1: string;
  md5: string;
  filename: string;
  file_type: string;
  arch: string;
  file_size: number;
  entropy: number;
  is_packed: boolean;
  packer_name: string;
  is_signed: boolean;
  risk_score: number;
  analyzed_at: string;
  analysis_status: string;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  risk_score: number;
  artifact_id: string | null;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
}

export interface AIMessage {
  role: "user" | "assistant";
  content: string;
  citations: Array<{ type: string; ref: string; label: string }>;
  ts: string;
}
