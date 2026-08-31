import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Database, Upload, CheckCircle, XCircle, Shield, RefreshCw } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import { evidenceApi, artifactsApi } from "../api/client";
import type { Evidence, Artifact } from "../types";

export default function EvidenceExplorer() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [evidenceType, setEvidenceType] = useState("filesystem_bundle");
  const [acquiredBy, setAcquiredBy] = useState("analyst");
  const [uploading, setUploading] = useState(false);

  const { data: evidence = [] } = useQuery({ queryKey: ["evidence", caseId], queryFn: () => evidenceApi.list(caseId!) });
  const { data: artifacts = [] } = useQuery({ queryKey: ["artifacts", caseId], queryFn: () => artifactsApi.list(caseId!) });

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !caseId) return;
    setUploading(true);
    try {
      await evidenceApi.upload(caseId, file, evidenceType, acquiredBy);
      qc.invalidateQueries({ queryKey: ["evidence", caseId] });
      qc.invalidateQueries({ queryKey: ["artifacts", caseId] });
      setFile(null);
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const evidenceCols = [
    { key: "original_filename", header: "Filename", sortable: true },
    { key: "evidence_type", header: "Type", render: (r: Evidence) => <span className="font-mono text-xs text-[#8b949e]">{r.evidence_type}</span> },
    { key: "sha256", header: "SHA-256", render: (r: Evidence) => <span className="hash-chip">{r.sha256.slice(0, 16)}…</span> },
    {
      key: "verification_ok", header: "Integrity",
      render: (r: Evidence) => (
        <span className={`badge ${r.verification_ok === "ok" ? "badge-ok" : r.verification_ok === "mismatch" ? "badge-critical" : "badge-low"}`}>
          {r.verification_ok}
        </span>
      )
    },
    { key: "size_bytes", header: "Size", render: (r: Evidence) => <span className="font-mono text-xs">{(r.size_bytes / 1024).toFixed(1)} KB</span>, sortable: true },
    { key: "acquired_by", header: "Acquired By" },
    { key: "acquired_at", header: "Acquired", render: (r: Evidence) => new Date(r.acquired_at).toLocaleString(), sortable: true },
  ];

  const artifactCols = [
    { key: "artifact_type", header: "Type", render: (r: Artifact) => <span className="font-mono text-xs text-[#58a6ff]">{r.artifact_type}</span> },
    { key: "name", header: "Name", sortable: true },
    { key: "path", header: "Path", mono: true },
    {
      key: "flagged_score", header: "Flags",
      render: (r: Artifact) => r.flagged_score > 0 ? (
        <span className="badge badge-critical" title={r.flagged_reason}>⚠ {r.flagged_score.toFixed(1)}</span>
      ) : <span className="text-[#484f58] text-xs">—</span>
    },
    {
      key: "labels", header: "Labels",
      render: (r: Artifact) => (
        <div className="flex gap-1 flex-wrap">
          {r.labels.map((l) => <span key={l} className={`badge ${l === "verified" ? "badge-ok" : "badge-low"}`}>{l}</span>)}
        </div>
      )
    },
  ];

  return (
    <PageWrapper title="Evidence Explorer" subtitle="Acquired evidence items and extracted artifacts">
      {/* Upload form */}
      <form onSubmit={handleUpload} className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Upload size={14} className="text-[#388bfd]" />
          <h2 className="text-sm font-semibold text-[#e6edf3]">Acquire Evidence</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-xs text-[#8b949e] mb-1.5">Evidence File</label>
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-xs rounded-lg px-3 py-2 file:mr-2 file:rounded file:bg-[#21262d] file:text-[#8b949e] file:border-0 file:text-xs"
              required />
          </div>
          <div>
            <label className="block text-xs text-[#8b949e] mb-1.5">Evidence Type</label>
            <select value={evidenceType} onChange={(e) => setEvidenceType(e.target.value)}
              className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]">
              <option value="filesystem_bundle">Filesystem Bundle</option>
              <option value="raw_image">Raw Image (DD)</option>
              <option value="e01">E01 Image</option>
              <option value="memory_dump">Memory Dump</option>
              <option value="pcap">PCAP Capture</option>
              <option value="registry_hive">Registry Hive</option>
              <option value="browser_profile">Browser Profile</option>
              <option value="single_file">Single File</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-[#8b949e] mb-1.5">Acquired By</label>
            <input value={acquiredBy} onChange={(e) => setAcquiredBy(e.target.value)}
              placeholder="analyst"
              className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]" />
          </div>
        </div>
        <button type="submit" disabled={uploading || !file}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#388bfd] text-white text-sm font-semibold hover:bg-[#1f6feb] disabled:opacity-50 transition-colors">
          {uploading ? <><RefreshCw size={14} className="animate-spin" /> Hashing & Parsing...</> : <><Shield size={14} /> Acquire & Parse</>}
        </button>
      </form>

      {/* Evidence table */}
      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58] flex items-center gap-2">
        <Database size={12} /> Evidence Items ({evidence.length})
      </div>
      <DataTable data={evidence} columns={evidenceCols} rowKey="id" maxHeight="300px" emptyMessage="No evidence acquired yet" />

      {/* Artifacts table */}
      <div className="mt-6 mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58] flex items-center gap-2">
        <Shield size={12} /> Extracted Artifacts ({artifacts.length})
      </div>
      <DataTable data={artifacts} columns={artifactCols} rowKey="id" emptyMessage="No artifacts extracted yet" />
    </PageWrapper>
  );
}
