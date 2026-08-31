import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Globe } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import { artifactsApi } from "../api/client";
import type { Artifact } from "../types";

export default function Browser() {
  const { caseId } = useParams<{ caseId: string }>();
  const { data: artifacts = [] } = useQuery({
    queryKey: ["artifacts", caseId, "browser"],
    queryFn: () => artifactsApi.list(caseId!, "browser"),
  });

  const columns = [
    { key: "artifact_type", header: "Type", render: (r: Artifact) => <span className="font-mono text-xs text-[#3fb950]">{r.artifact_type}</span> },
    { key: "name", header: "Entry", sortable: true, render: (r: Artifact) => <span className="font-semibold">{r.name}</span> },
    { key: "path", header: "URL / Path", render: (r: Artifact) => <span className="font-mono text-[10px] text-[#58a6ff] truncate max-w-xs block" title={r.path}>{r.path}</span> },
    { key: "user", header: "Profile" },
    { key: "created_ts", header: "Visited", render: (r: Artifact) => r.created_ts ? new Date(r.created_ts).toLocaleString() : "—" },
    {
      key: "flagged_score", header: "Risk",
      render: (r: Artifact) => r.flagged_score > 0
        ? <span className="badge badge-critical">⚠ {r.flagged_score.toFixed(1)}</span>
        : <span className="text-[#484f58]">—</span>
    },
  ];

  return (
    <PageWrapper
      title="Browser Forensics"
      subtitle="Browsing history, cookies, downloads, saved credentials, and extensions"
    >
      <div className="text-xs text-[#484f58] mb-4 flex items-center gap-2">
        <Globe size={12} /> {artifacts.length} browser artifacts
      </div>
      <DataTable data={artifacts} columns={columns} rowKey="id" emptyMessage="No browser artifacts. Acquire a browser profile to analyze." />
    </PageWrapper>
  );
}
