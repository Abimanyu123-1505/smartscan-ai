import { Shield, Database, Bell, User, Server, Eye } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";

export default function Settings() {
  return (
    <PageWrapper title="Settings" subtitle="Platform configuration and preferences">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform info */}
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Server size={14} className="text-[#388bfd]" />
            <h2 className="text-sm font-semibold">Platform Information</h2>
          </div>
          <div className="space-y-3">
            {[
              ["Version", "DFIOP v2.0.0"],
              ["Backend", "FastAPI + SQLAlchemy"],
              ["Database", "SQLite (dev) / PostgreSQL (prod)"],
              ["Auth", "JWT + RBAC"],
              ["Evidence Mode", "Read-only acquisition"],
              ["Chain of Custody", "SHA-256 hash chain"],
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between text-sm border-b border-[#21262d] pb-2 last:border-0">
                <span className="text-[#8b949e]">{label}</span>
                <span className="font-mono text-xs text-[#e6edf3]">{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Capabilities */}
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={14} className="text-[#388bfd]" />
            <h2 className="text-sm font-semibold">Installed Modules</h2>
          </div>
          <div className="space-y-2">
            {[
              ["Case Management", true],
              ["Evidence Acquisition", true],
              ["Disk Forensics", true],
              ["Memory Forensics (Volatility3)", true],
              ["Network Analysis (PCAP)", true],
              ["Registry Analysis", true],
              ["Browser Forensics", true],
              ["YARA Engine", true],
              ["Sigma Detection", true],
              ["IOC Hunting", true],
              ["MITRE ATT&CK Mapping", true],
              ["Malware Analysis", true],
              ["AI RAG Assistant", true],
              ["Entity Graph", true],
              ["Reporting & Export", true],
            ].map(([name, enabled]) => (
              <div key={String(name)} className="flex items-center justify-between py-1">
                <span className="text-sm text-[#e6edf3]">{name}</span>
                <span className={`badge ${enabled ? "badge-ok" : "badge-low"}`}>{enabled ? "Active" : "Inactive"}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
