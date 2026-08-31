// Typed API client for DFIOP
import type {
  Case, Evidence, Artifact, TimelineEvent, AuditLog, SearchResult,
  DashboardStats, IOC, IOCMatch, YARARule, YARAMatch, SigmaRule, SigmaRuleCreate, SigmaAlert,
  MITRETactic, MITREMapping, MemoryArtifact, NetworkArtifact, RegistryKey,
  MalwareSample, GraphNode, GraphEdge
} from "../types";

const BASE = "/api";
const V1 = "/api/v1";

async function req<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardApi = {
  stats: () => req<DashboardStats>(`${V1}/dashboard/stats`),
  caseTrend: () => req<{ trend: { date: string; count: number }[] }>(`${V1}/dashboard/case-trend`),
  evidenceTypes: () => req<{ types: { type: string; count: number }[] }>(`${V1}/dashboard/evidence-types`),
  artifactTypes: () => req<{ types: { type: string; count: number }[] }>(`${V1}/dashboard/artifact-types`),
  recentActivity: () => req<{ activity: { actor: string; action: string; detail: string; timestamp: string }[] }>(`${V1}/dashboard/recent-activity`),
};

// ── Cases ─────────────────────────────────────────────────────────────────────
export const casesApi = {
  list: () => req<Case[]>(`${BASE}/cases`),
  get: (id: string) => req<Case>(`${BASE}/cases/${id}`),
  create: (payload: Partial<Case>) => req<Case>(`${BASE}/cases`, { method: "POST", body: JSON.stringify(payload) }),
  update: (id: string, payload: Partial<Case>) => req<Case>(`${BASE}/cases/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  auditLog: (id: string) => req<AuditLog[]>(`${BASE}/cases/${id}/audit-log`),
  verifyChain: (id: string) => req<{ ok: boolean; checked: number; broken_at?: number }>(`${BASE}/cases/${id}/audit-log/verify`),
};

// ── Evidence ──────────────────────────────────────────────────────────────────
export const evidenceApi = {
  list: (caseId: string) => req<Evidence[]>(`${BASE}/cases/${caseId}/evidence`),
  upload: async (caseId: string, file: File, evidenceType: string, acquiredBy: string) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("evidence_type", evidenceType);
    fd.append("acquired_by", acquiredBy);
    const res = await fetch(`${BASE}/cases/${caseId}/evidence`, { method: "POST", body: fd });
    if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
    return res.json() as Promise<Evidence>;
  },
  reverify: (evidenceId: string) => req<Evidence>(`${BASE}/evidence/${evidenceId}/verify`, { method: "POST" }),
};

// ── Artifacts ─────────────────────────────────────────────────────────────────
export const artifactsApi = {
  list: (caseId: string, type?: string) =>
    req<Artifact[]>(`${BASE}/cases/${caseId}/artifacts${type ? `?artifact_type=${type}` : ""}`),
  label: (artifactId: string, label: string, verifiedBy?: string) =>
    req<Artifact>(`${BASE}/artifacts/${artifactId}/label`, {
      method: "POST",
      body: JSON.stringify({ label, verified_by: verifiedBy }),
    }),
};

// ── Timeline ──────────────────────────────────────────────────────────────────
export const timelineApi = {
  list: (caseId: string) => req<TimelineEvent[]>(`${BASE}/cases/${caseId}/timeline`),
};

// ── Search ────────────────────────────────────────────────────────────────────
export const searchApi = {
  search: (caseId: string, q: string) =>
    req<SearchResult[]>(`${BASE}/cases/${caseId}/search?q=${encodeURIComponent(q)}`),
};

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportsApi = {
  pdfUrl: (caseId: string) => `${BASE}/cases/${caseId}/report.pdf`,
};

// ── IOC ───────────────────────────────────────────────────────────────────────
export const iocApi = {
  list: (caseId: string) => req<IOC[]>(`${V1}/cases/${caseId}/iocs`),
  create: (caseId: string, payload: Partial<IOC>) =>
    req<IOC>(`${V1}/cases/${caseId}/iocs`, { method: "POST", body: JSON.stringify(payload) }),
  scan: (caseId: string) => req<{ matches_created: number }>(`${V1}/cases/${caseId}/iocs/scan`, { method: "POST" }),
  matches: (caseId: string) => req<IOCMatch[]>(`${V1}/cases/${caseId}/ioc-matches`),
  delete: (caseId: string, iocId: string) => req(`${V1}/cases/${caseId}/iocs/${iocId}`, { method: "DELETE" }),
};

// ── YARA ──────────────────────────────────────────────────────────────────────
export const yaraApi = {
  rules: () => req<YARARule[]>(`${V1}/yara/rules`),
  createRule: (payload: Partial<YARARule>) =>
    req<YARARule>(`${V1}/yara/rules`, { method: "POST", body: JSON.stringify(payload) }),
  scan: (caseId: string) => req<{ matches: number }>(`${V1}/cases/${caseId}/yara/scan`, { method: "POST" }),
  matches: (caseId: string) => req<YARAMatch[]>(`${V1}/cases/${caseId}/yara/matches`),
  deleteRule: (ruleId: string) => req(`${V1}/yara/rules/${ruleId}`, { method: "DELETE" }),
};

// ── Sigma ─────────────────────────────────────────────────────────────────────
export const sigmaApi = {
  rules: () => req<SigmaRule[]>(`${V1}/sigma/rules`),
  createRule: (payload: SigmaRuleCreate) =>
    req<SigmaRule>(`${V1}/sigma/rules`, { method: "POST", body: JSON.stringify(payload) }),
  run: (caseId: string) => req<{ alerts_created: number }>(`${V1}/cases/${caseId}/sigma/run`, { method: "POST" }),
  alerts: (caseId: string) => req<SigmaAlert[]>(`${V1}/cases/${caseId}/sigma/alerts`),
  acknowledge: (caseId: string, alertId: string) =>
    req(`${V1}/cases/${caseId}/sigma/alerts/${alertId}/acknowledge`, { method: "POST" }),
};

// ── MITRE ─────────────────────────────────────────────────────────────────────
export const mitreApi = {
  matrix: () => req<{ tactics: MITRETactic[] }>(`${V1}/mitre/matrix`),
  mappings: (caseId: string) => req<MITREMapping[]>(`${V1}/cases/${caseId}/mitre/mappings`),
  heatmap: (caseId: string) => req<{ heatmap: { technique_id: string; count: number }[] }>(`${V1}/cases/${caseId}/mitre/heatmap`),
};

// ── Memory ────────────────────────────────────────────────────────────────────
export const memoryApi = {
  analyze: (caseId: string) => req<{ artifacts_extracted: number }>(`${V1}/cases/${caseId}/memory/analyze`, { method: "POST" }),
  processes: (caseId: string) => req<MemoryArtifact[]>(`${V1}/cases/${caseId}/memory/processes`),
  summary: (caseId: string) => req<{ total: number; suspicious: number; hidden: number; injected: number }>(`${V1}/cases/${caseId}/memory/summary`),
};

// ── Network ───────────────────────────────────────────────────────────────────
export const networkApi = {
  analyze: (caseId: string) => req<{ connections: number }>(`${V1}/cases/${caseId}/network/analyze`, { method: "POST" }),
  connections: (caseId: string) => req<NetworkArtifact[]>(`${V1}/cases/${caseId}/network/connections`),
  summary: (caseId: string) => req<{ total: number; flagged: number; protocols: { protocol: string; count: number }[] }>(`${V1}/cases/${caseId}/network/summary`),
};

// ── Registry ──────────────────────────────────────────────────────────────────
export const registryApi = {
  parse: (caseId: string) => req<{ keys_extracted: number }>(`${V1}/cases/${caseId}/registry/parse`, { method: "POST" }),
  keys: (caseId: string, params?: { hive?: string; category?: string; flagged_only?: boolean }) => {
    const qs = new URLSearchParams();
    if (params?.hive) qs.set("hive", params.hive);
    if (params?.category) qs.set("category", params.category);
    if (params?.flagged_only) qs.set("flagged_only", "true");
    return req<RegistryKey[]>(`${V1}/cases/${caseId}/registry/keys?${qs}`);
  },
  summary: (caseId: string) => req<{ total: number; flagged: number; by_hive: { hive: string; count: number }[] }>(`${V1}/cases/${caseId}/registry/summary`),
};

// ── Malware ───────────────────────────────────────────────────────────────────
export const malwareApi = {
  analyze: (caseId: string) => req<{ analyzed: number }>(`${V1}/cases/${caseId}/malware/analyze`, { method: "POST" }),
  samples: (caseId: string) => req<MalwareSample[]>(`${V1}/cases/${caseId}/malware/samples`),
  sample: (caseId: string, sampleId: string) => req<MalwareSample & { sections: unknown[]; imports: unknown[]; strings: string[]; suspicious_apis: string[] }>(`${V1}/cases/${caseId}/malware/samples/${sampleId}`),
};

// ── Graph ─────────────────────────────────────────────────────────────────────
export const graphApi = {
  build: (caseId: string) => req<{ nodes_created: number }>(`${V1}/cases/${caseId}/graph/build`, { method: "POST" }),
  get: (caseId: string) => req<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`${V1}/cases/${caseId}/graph`),
};

// ── AI ────────────────────────────────────────────────────────────────────────
export const aiApi = {
  chat: (caseId: string, message: string, sessionId?: string) =>
    req<{ session_id: string; role: string; content: string; citations: unknown[]; timestamp: string }>(
      `${V1}/cases/${caseId}/ai/chat`,
      { method: "POST", body: JSON.stringify({ message, session_id: sessionId }) }
    ),
  session: (caseId: string, sessionId: string) =>
    req<{ session_id: string; messages: unknown[] }>(`${V1}/cases/${caseId}/ai/sessions/${sessionId}`),
};
