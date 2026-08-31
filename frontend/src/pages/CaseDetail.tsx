import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Database, Clock, Search, HardDrive, Brain, Layers, Globe,
  Network, Shield, Zap, AlertTriangle, Map, GitBranch, Bot,
  FileText, ChevronRight, Flag, Activity
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { casesApi } from "../api/client";
import { useAppStore } from "../stores/appStore";

interface ModuleCard {
  path: string;
  label: string;
  description: string;
  icon: LucideIcon;
  color: string;
  group: string;
}

const MODULES: ModuleCard[] = [
  { path: "evidence", label: "Evidence Explorer", description: "Browse and verify acquired evidence items", icon: Database, color: "#d29922", group: "Investigation" },
  { path: "timeline", label: "Timeline", description: "Unified event timeline across all artifact sources", icon: Clock, color: "#39d353", group: "Investigation" },
  { path: "search", label: "Search", description: "Full-text search across all extracted artifacts", icon: Search, color: "#388bfd", group: "Investigation" },
  { path: "disk", label: "Disk Forensics", description: "MFT, partitions, deleted files, ADS analysis", icon: HardDrive, color: "#8b949e", group: "Forensics" },
  { path: "memory", label: "Memory Forensics", description: "Volatility3 process, DLL, and network analysis", icon: Brain, color: "#bc8cff", group: "Forensics" },
  { path: "registry", label: "Registry Analysis", description: "Windows registry hive parsing and Run keys", icon: Layers, color: "#58a6ff", group: "Forensics" },
  { path: "browser", label: "Browser Forensics", description: "History, cookies, downloads, extensions", icon: Globe, color: "#388bfd", group: "Forensics" },
  { path: "network", label: "Network Forensics", description: "PCAP analysis, DNS, HTTP, TLS connections", icon: Network, color: "#e3b341", group: "Forensics" },
  { path: "malware", label: "Malware Analysis", description: "PE/ELF analysis, imports, entropy, strings", icon: Shield, color: "#f85149", group: "Detection" },
  { path: "yara", label: "YARA Scanning", description: "Upload and run YARA rules across evidence", icon: Zap, color: "#d29922", group: "Detection" },
  { path: "sigma", label: "Sigma Detection", description: "Run Sigma rules against event logs", icon: AlertTriangle, color: "#e3b341", group: "Detection" },
  { path: "ioc", label: "IOC Hunting", description: "Search case artifacts for indicators of compromise", icon: Map, color: "#f85149", group: "Detection" },
  { path: "mitre", label: "MITRE ATT&CK", description: "ATT&CK matrix heatmap and technique mapping", icon: GitBranch, color: "#bc8cff", group: "Detection" },
  { path: "graph", label: "Entity Graph", description: "Interactive relationship graph of case entities", icon: GitBranch, color: "#39d353", group: "Analysis" },
  { path: "ai", label: "AI Assistant", description: "Case-aware RAG investigation assistant", icon: Bot, color: "#bc8cff", group: "Analysis" },
  { path: "reports", label: "Reports", description: "Generate PDF, HTML, and Markdown reports", icon: FileText, color: "#388bfd", group: "Output" },
];

const groupColors: Record<string, string> = {
  Investigation: "#388bfd",
  Forensics: "#8b949e",
  Detection: "#f85149",
  Analysis: "#bc8cff",
  Output: "#3fb950",
};

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const setActiveCase = useAppStore((s) => s.setActiveCase);

  const { data: caseData } = useQuery({
    queryKey: ["case", caseId],
    queryFn: () => casesApi.get(caseId!),
    enabled: !!caseId,
  });

  const { data: chainStatus } = useQuery({
    queryKey: ["chain", caseId],
    queryFn: () => casesApi.verifyChain(caseId!),
    enabled: !!caseId,
  });

  useEffect(() => {
    if (caseData) setActiveCase(caseData);
    return () => setActiveCase(null);
  }, [caseData, setActiveCase]);

  if (!caseData) return <div className="text-[#484f58] py-12 text-center">Loading case...</div>;

  const groups = MODULES.reduce((acc, m) => {
    if (!acc[m.group]) acc[m.group] = [];
    acc[m.group].push(m);
    return acc;
  }, {} as Record<string, ModuleCard[]>);

  const priorityColor: Record<string, string> = { critical: "#f85149", high: "#d29922", medium: "#388bfd", low: "#3fb950" };

  return (
    <PageWrapper>
      {/* Case header */}
      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-[#e6edf3] font-display">{caseData.name}</h1>
              <span className="font-mono text-xs text-[#d29922] bg-[rgba(210,153,34,0.1)] px-2 py-1 rounded">
                CASE-{caseData.id.toUpperCase()}
              </span>
              <span
                className="text-[10px] font-bold uppercase px-2 py-1 rounded"
                style={{ color: priorityColor[caseData.priority], background: `${priorityColor[caseData.priority]}20` }}
              >
                {caseData.priority}
              </span>
            </div>
            {caseData.description && (
              <p className="text-sm text-[#8b949e] mb-3">{caseData.description}</p>
            )}
            <div className="flex items-center gap-4 text-xs text-[#484f58] font-mono">
              <span>Investigator: <span className="text-[#8b949e]">{caseData.investigator || "Unassigned"}</span></span>
              <span>Created: {new Date(caseData.created_at).toLocaleDateString()}</span>
              {caseData.incident_type && <span>Type: {caseData.incident_type}</span>}
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            {chainStatus && (
              <div className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg ${
                chainStatus.ok
                  ? "bg-[rgba(63,185,80,0.1)] text-[#3fb950] border border-[rgba(63,185,80,0.2)]"
                  : "bg-[rgba(248,81,73,0.1)] text-[#f85149] border border-[rgba(248,81,73,0.2)]"
              }`}>
                <Activity size={12} />
                {chainStatus.ok ? "Chain intact" : "Chain broken"}
              </div>
            )}
            <div className="text-[10px] text-[#484f58] font-mono">
              Risk: <span className="text-[#d29922]">{caseData.risk_score.toFixed(0)}/100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Module grid */}
      {Object.entries(groups).map(([group, modules]) => (
        <div key={group} className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full" style={{ background: groupColors[group] }} />
            <h2 className="text-xs font-semibold uppercase tracking-widest text-[#8b949e]">{group}</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {modules.map((m) => (
              <motion.div key={m.path} whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }}>
                <Link
                  to={`/cases/${caseId}/${m.path}`}
                  className="flex items-start gap-3 p-4 bg-[#161b22] border border-[#21262d] rounded-xl hover:border-[#30363d] transition-all group block"
                >
                  <div
                    className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-all"
                    style={{ background: `${m.color}15`, border: `1px solid ${m.color}30` }}
                  >
                    <m.icon size={16} className="transition-colors" style={{ color: m.color }} />
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-[#e6edf3] mb-0.5 group-hover:text-white">{m.label}</div>
                    <div className="text-[11px] text-[#484f58] leading-relaxed">{m.description}</div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      ))}
    </PageWrapper>
  );
}
