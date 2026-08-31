import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { GitBranch } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { mitreApi } from "../api/client";

export default function MITRE() {
  const { caseId } = useParams<{ caseId: string }>();

  const { data: matrix } = useQuery({ queryKey: ["mitre-matrix"], queryFn: mitreApi.matrix });
  const { data: mappings = [] } = useQuery({ queryKey: ["mitre-mappings", caseId], queryFn: () => mitreApi.mappings(caseId!) });
  const { data: heatmap } = useQuery({ queryKey: ["mitre-heatmap", caseId], queryFn: () => mitreApi.heatmap(caseId!) });

  const hitSet = new Set(heatmap?.heatmap.filter((h) => h.count > 0).map((h) => h.technique_id));

  return (
    <PageWrapper title="MITRE ATT&CK" subtitle="Technique mapping and tactic coverage across this investigation">
      {/* Heatmap matrix */}
      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 mb-6 overflow-x-auto">
        <div className="flex items-center gap-2 mb-4">
          <GitBranch size={14} className="text-[#bc8cff]" />
          <h2 className="text-sm font-semibold text-[#e6edf3]">ATT&CK Matrix</h2>
          <span className="text-xs text-[#484f58]">— highlighted techniques were observed in this case</span>
        </div>
        <div className="flex gap-3" style={{ minWidth: "max-content" }}>
          {(matrix?.tactics ?? []).map((tactic) => (
            <div key={tactic.id} className="min-w-[130px]">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[#8b949e] mb-2 pb-1 border-b border-[#21262d] text-center">
                {tactic.name}
              </div>
              <div className="space-y-1">
                {tactic.techniques.map((tech) => {
                  const hit = hitSet.has(tech.id);
                  return (
                    <div
                      key={tech.id}
                      className={`px-2 py-1.5 rounded text-[10px] font-mono transition-all cursor-default ${
                        hit
                          ? "bg-[rgba(248,81,73,0.2)] text-[#f85149] border border-[rgba(248,81,73,0.3)] font-bold"
                          : "bg-[#0d1117] text-[#484f58] border border-transparent hover:border-[#30363d] hover:text-[#8b949e]"
                      }`}
                      title={`${tech.id}: ${tech.name}`}
                    >
                      <div>{tech.id}</div>
                      <div className="text-[9px] truncate">{tech.name}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mappings table */}
      {mappings.length > 0 && (
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
          <h2 className="text-sm font-semibold text-[#e6edf3] mb-4">Case Technique Mappings</h2>
          <div className="space-y-2">
            {mappings.map((m) => (
              <div key={m.id} className="flex items-center gap-4 py-2 border-b border-[#21262d] last:border-0">
                <span className="font-mono text-[11px] text-[#bc8cff] bg-[rgba(188,140,255,0.1)] px-2 py-0.5 rounded shrink-0">{m.technique_id}</span>
                <span className="text-sm text-[#e6edf3]">{m.technique_name}</span>
                <span className="text-xs text-[#484f58]">{m.tactic}</span>
                <span className="ml-auto text-xs text-[#484f58] font-mono">confidence: {(m.confidence * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </PageWrapper>
  );
}
