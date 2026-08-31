import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { HardDrive } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import { artifactsApi } from "../api/client";
import type { Artifact } from "../types";

export default function Disk() {
  const { caseId } = useParams<{ caseId: string }>();
  const { data: artifacts = [] } = useQuery({
    queryKey: ["artifacts", caseId, "filesystem"],
    queryFn: () => artifactsApi.list(caseId!, "filesystem"),
  });

  const columns = [
    { key: "name", header: "Name", sortable: true, render: (r: Artifact) => <span className="font-semibold">{r.name}</span> },
    { key: "path", header: "Path", mono: true, render: (r: Artifact) => <span className="font-mono text-[10px] text-[#8b949e]">{r.path}</span> },
    { key: "operation", header: "Op", render: (r: Artifact) => <span className="font-mono text-xs uppercase text-[#d29922]">{r.operation}</span> },
    { key: "sha256", header: "SHA-256", render: (r: Artifact) => <span className="hash-chip">{r.sha256.slice(0, 16)}…</span> },
    { key: "size_bytes", header: "Size", render: (r: Artifact) => <span className="font-mono text-xs">{(r.size_bytes / 1024).toFixed(1)} KB</span>, sortable: true },
    { key: "user", header: "Owner" },
    { key: "created_ts", header: "Created", render: (r: Artifact) => r.created_ts ? new Date(r.created_ts).toLocaleString() : "—", sortable: true },
    {
      key: "flagged_score", header: "Flags",
      render: (r: Artifact) => r.flagged_score > 0
        ? <span className="badge badge-critical">⚠ {r.flagged_score.toFixed(1)}</span>
        : <span className="text-[#484f58] text-xs">—</span>
    },
  ];

  return (
    <PageWrapper
      title="Disk Forensics"
      subtitle="MFT, NTFS metadata, deleted files, alternate data streams, and file system artifacts"
    >
      <div className="text-xs text-[#484f58] mb-4 flex items-center gap-2">
        <HardDrive size={12} /> {artifacts.length} filesystem artifacts extracted
      </div>
      <DataTable data={artifacts} columns={columns} rowKey="id"
        emptyMessage="No filesystem artifacts yet. Acquire a disk image and parse evidence." />
    </PageWrapper>
  );
}
