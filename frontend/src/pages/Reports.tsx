import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { FileText, Download, ExternalLink, CheckCircle } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { casesApi, reportsApi } from "../api/client";

export default function Reports() {
  const { caseId } = useParams<{ caseId: string }>();

  const { data: caseData } = useQuery({
    queryKey: ["case", caseId],
    queryFn: () => casesApi.get(caseId!),
    enabled: !!caseId,
  });

  const { data: auditLog = [] } = useQuery({
    queryKey: ["audit", caseId],
    queryFn: () => casesApi.auditLog(caseId!),
    enabled: !!caseId,
  });

  const { data: chainStatus } = useQuery({
    queryKey: ["chain", caseId],
    queryFn: () => casesApi.verifyChain(caseId!),
    enabled: !!caseId,
  });

  const pdfUrl = caseId ? reportsApi.pdfUrl(caseId) : "#";

  return (
    <PageWrapper title="Reports & Chain of Custody" subtitle="Generate investigation reports and verify evidence chain integrity">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Report export */}
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <FileText size={14} className="text-[#388bfd]" />
            <h2 className="text-sm font-semibold text-[#e6edf3]">Export Report</h2>
          </div>
          <p className="text-xs text-[#8b949e] mb-4">
            Generate a comprehensive forensic investigation report including case metadata,
            artifact inventory, timeline, MITRE mappings, IOC hits, and chain-of-custody.
          </p>
          {caseData && (
            <div className="bg-[#0d1117] rounded-lg p-3 mb-4 space-y-1.5 text-xs font-mono">
              <div><span className="text-[#484f58]">Case: </span><span className="text-[#d29922]">{caseData.name}</span></div>
              <div><span className="text-[#484f58]">ID: </span><span className="text-[#8b949e]">{caseData.id}</span></div>
              <div><span className="text-[#484f58]">Status: </span><span className="text-[#3fb950]">{caseData.status}</span></div>
              <div><span className="text-[#484f58]">Investigator: </span><span className="text-[#8b949e]">{caseData.investigator}</span></div>
            </div>
          )}
          <div className="flex gap-3">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#388bfd] text-white text-sm font-semibold hover:bg-[#1f6feb] transition-colors"
            >
              <Download size={14} />Download PDF
            </a>
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm hover:border-[#388bfd] hover:text-[#388bfd] transition-colors"
            >
              <ExternalLink size={14} />Preview
            </a>
          </div>
        </div>

        {/* Chain of custody */}
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={14} className={chainStatus?.ok ? "text-[#3fb950]" : "text-[#f85149]"} />
            <h2 className="text-sm font-semibold text-[#e6edf3]">Chain of Custody</h2>
            {chainStatus && (
              <span className={`ml-auto badge ${chainStatus.ok ? "badge-ok" : "badge-critical"}`}>
                {chainStatus.ok ? `${chainStatus.checked} entries verified` : "BROKEN"}
              </span>
            )}
          </div>
          <p className="text-xs text-[#8b949e] mb-4">
            Each audit log entry is cryptographically chained — any tampering breaks the hash chain.
          </p>
          <div className="max-h-60 overflow-y-auto space-y-1">
            {auditLog.slice(0, 20).map((entry) => (
              <div key={entry.id} className="flex items-start gap-3 py-2 border-b border-[#21262d] last:border-0">
                <div className="w-1.5 h-1.5 mt-1.5 rounded-full bg-[#3fb950] shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs font-medium text-[#58a6ff]">{entry.actor}</span>
                    <span className="text-xs text-[#e6edf3]">{entry.action.replace(/_/g, " ")}</span>
                  </div>
                  <div className="font-mono text-[10px] text-[#484f58] truncate">{entry.entry_hash.slice(0, 32)}…</div>
                </div>
                <span className="text-[10px] text-[#484f58] font-mono shrink-0">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
            {auditLog.length === 0 && (
              <div className="text-center py-6 text-[#484f58] text-xs">No audit entries yet.</div>
            )}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
