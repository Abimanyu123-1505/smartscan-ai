import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Network as NetworkIcon, Play, AlertTriangle, Globe, Shield } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import StatCard from "../components/shared/StatCard";
import { networkApi } from "../api/client";
import type { NetworkArtifact } from "../types";

export default function Network() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();

  const { data: summary } = useQuery({ queryKey: ["network-summary", caseId], queryFn: () => networkApi.summary(caseId!) });
  const { data: connections = [] } = useQuery({ queryKey: ["network-connections", caseId], queryFn: () => networkApi.connections(caseId!) });

  const analyzeMutation = useMutation({
    mutationFn: () => networkApi.analyze(caseId!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["network-connections", caseId] });
      qc.invalidateQueries({ queryKey: ["network-summary", caseId] });
    },
  });

  const columns = [
    { key: "protocol", header: "Protocol", render: (r: NetworkArtifact) => <span className="font-mono text-xs font-bold text-[#e3b341]">{r.protocol}</span> },
    { key: "src_ip", header: "Source", render: (r: NetworkArtifact) => <span className="font-mono text-xs">{r.src_ip}:{r.src_port}</span>, mono: true },
    { key: "dst_ip", header: "Destination", render: (r: NetworkArtifact) => (
      <div>
        <div className="font-mono text-xs">{r.dst_ip}:{r.dst_port}</div>
        {r.hostname && <div className="text-xs text-[#58a6ff]">{r.hostname}</div>}
      </div>
    )},
    { key: "bytes_sent", header: "Sent", render: (r: NetworkArtifact) => <span className="font-mono text-xs">{(r.bytes_sent / 1024).toFixed(1)}KB</span>, sortable: true },
    { key: "bytes_recv", header: "Recv", render: (r: NetworkArtifact) => <span className="font-mono text-xs">{(r.bytes_recv / 1024).toFixed(1)}KB</span>, sortable: true },
    { key: "flagged", header: "Status", render: (r: NetworkArtifact) => r.flagged ? (
      <span className="badge badge-critical" title={r.flag_reason}>⚠ Flagged</span>
    ) : <span className="badge badge-ok">Clean</span> },
    { key: "flag_reason", header: "Reason", render: (r: NetworkArtifact) => <span className="text-xs text-[#8b949e]">{r.flag_reason || "—"}</span> },
  ];

  return (
    <PageWrapper
      title="Network Forensics"
      subtitle="PCAP analysis — DNS, HTTP, TLS, SMB, FTP connections and flow reconstruction"
      actions={
        <button onClick={() => analyzeMutation.mutate()} disabled={analyzeMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#e3b341] text-[#0d1117] text-sm font-semibold hover:opacity-90 disabled:opacity-50">
          <Play size={14} />{analyzeMutation.isPending ? "Analyzing..." : "Analyze PCAP"}
        </button>
      }
    >
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Total Connections" value={summary?.total ?? 0} icon={NetworkIcon} color="amber" />
        <StatCard label="Flagged" value={summary?.flagged ?? 0} icon={AlertTriangle} color="red" />
        <StatCard label="Protocols" value={summary?.protocols?.length ?? 0} icon={Globe} color="blue" />
      </div>
      <DataTable data={connections} columns={columns} rowKey="id" emptyMessage="No network data. Acquire PCAP evidence and run analysis." />
    </PageWrapper>
  );
}
