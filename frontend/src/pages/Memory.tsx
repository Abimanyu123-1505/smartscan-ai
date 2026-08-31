import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Play, AlertTriangle, Eye, Cpu } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import StatCard from "../components/shared/StatCard";
import { memoryApi } from "../api/client";
import type { MemoryArtifact } from "../types";

export default function Memory() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();

  const { data: summary } = useQuery({ queryKey: ["memory-summary", caseId], queryFn: () => memoryApi.summary(caseId!) });
  const { data: processes = [] } = useQuery({ queryKey: ["memory-processes", caseId], queryFn: () => memoryApi.processes(caseId!) });

  const analyzeMutation = useMutation({
    mutationFn: () => memoryApi.analyze(caseId!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["memory-processes", caseId] });
      qc.invalidateQueries({ queryKey: ["memory-summary", caseId] });
    },
  });

  const columns = [
    { key: "pid", header: "PID", render: (r: MemoryArtifact) => <span className="font-mono text-[#58a6ff]">{r.pid}</span>, sortable: true },
    { key: "ppid", header: "PPID", render: (r: MemoryArtifact) => <span className="font-mono text-[#484f58]">{r.ppid}</span> },
    { key: "name", header: "Process", render: (r: MemoryArtifact) => (
      <span className={r.suspicious ? "text-[#f85149] font-semibold" : "text-[#e6edf3]"}>{r.name}</span>
    ), sortable: true },
    { key: "path", header: "Path", mono: true },
    { key: "command_line", header: "Command Line", render: (r: MemoryArtifact) => (
      <span className="font-mono text-xs text-[#8b949e] truncate max-w-xs block" title={r.command_line}>{r.command_line || "—"}</span>
    )},
    { key: "flags", header: "Flags", render: (r: MemoryArtifact) => (
      <div className="flex gap-1">
        {r.suspicious && <span className="badge badge-critical">Suspicious</span>}
        {r.hidden && <span className="badge badge-critical">Hidden</span>}
        {r.injected && <span className="badge badge-high">Injected</span>}
        {!r.suspicious && !r.hidden && !r.injected && <span className="text-[#484f58] text-xs">—</span>}
      </div>
    )},
  ];

  return (
    <PageWrapper
      title="Memory Forensics"
      subtitle="Volatility3-powered memory analysis — processes, DLLs, connections, and injected code"
      actions={
        <button
          onClick={() => analyzeMutation.mutate()}
          disabled={analyzeMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#bc8cff] text-[#0d1117] text-sm font-semibold hover:opacity-90 disabled:opacity-50 transition-all"
        >
          <Play size={14} />
          {analyzeMutation.isPending ? "Analyzing..." : "Run Analysis"}
        </button>
      }
    >
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Processes" value={summary?.total ?? 0} icon={Cpu} color="purple" />
        <StatCard label="Suspicious" value={summary?.suspicious ?? 0} icon={AlertTriangle} color="red" />
        <StatCard label="Hidden" value={summary?.hidden ?? 0} icon={Eye} color="red" />
        <StatCard label="Injected" value={summary?.injected ?? 0} icon={Brain} color="amber" />
      </div>
      <DataTable data={processes} columns={columns} rowKey="id" emptyMessage="No memory artifacts. Run Analysis to extract process list." />
    </PageWrapper>
  );
}
