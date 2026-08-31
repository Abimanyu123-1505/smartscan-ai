import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Map, Plus, Play, Trash2, AlertCircle } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import { iocApi } from "../api/client";
import type { IOC, IOCMatch } from "../types";

const IOC_TYPES = ["ip", "domain", "url", "md5", "sha1", "sha256", "email", "filename", "registry_key", "useragent"];

export default function IOC() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ioc_type: "ip", value: "", description: "", source: "analyst", risk_score: 50 });

  const { data: iocs = [] } = useQuery({ queryKey: ["iocs", caseId], queryFn: () => iocApi.list(caseId!) });
  const { data: matches = [] } = useQuery({ queryKey: ["ioc-matches", caseId], queryFn: () => iocApi.matches(caseId!) });

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => iocApi.create(caseId!, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["iocs", caseId] }); setShowForm(false); setForm({ ioc_type: "ip", value: "", description: "", source: "analyst", risk_score: 50 }); },
  });

  const scanMutation = useMutation({
    mutationFn: () => iocApi.scan(caseId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ioc-matches", caseId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (iocId: string) => iocApi.delete(caseId!, iocId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["iocs", caseId] }),
  });

  const iocCols = [
    { key: "ioc_type", header: "Type", render: (r: IOC) => <span className="font-mono text-xs font-bold text-[#e3b341] uppercase">{r.ioc_type}</span> },
    { key: "value", header: "Indicator", render: (r: IOC) => <span className="font-mono text-xs text-[#e6edf3]">{r.value}</span> },
    { key: "description", header: "Description" },
    { key: "source", header: "Source", render: (r: IOC) => <span className="text-xs text-[#8b949e]">{r.source}</span> },
    { key: "risk_score", header: "Risk", render: (r: IOC) => (
      <span className={`badge ${r.risk_score >= 70 ? "badge-critical" : r.risk_score >= 40 ? "badge-high" : "badge-low"}`}>
        {r.risk_score.toFixed(0)}
      </span>
    ), sortable: true },
    { key: "confirmed", header: "Confirmed", render: (r: IOC) => r.confirmed ? <span className="badge badge-ok">Yes</span> : <span className="badge badge-low">No</span> },
    { key: "actions", header: "", render: (r: IOC) => (
      <button onClick={() => deleteMutation.mutate(r.id)} className="p-1 text-[#484f58] hover:text-[#f85149] transition-colors">
        <Trash2 size={14} />
      </button>
    )},
  ];

  const matchCols = [
    { key: "ioc_id", header: "IOC ID", mono: true, render: (r: IOCMatch) => <span className="hash-chip">{r.ioc_id.slice(0, 8)}</span> },
    { key: "artifact_id", header: "Artifact", mono: true },
    { key: "match_context", header: "Context", render: (r: IOCMatch) => <span className="font-mono text-xs text-[#8b949e]">{r.match_context}</span> },
    { key: "matched_at", header: "Matched At", render: (r: IOCMatch) => new Date(r.matched_at).toLocaleString() },
  ];

  return (
    <PageWrapper
      title="IOC Hunting"
      subtitle="Add indicators of compromise and scan case artifacts for matches"
      actions={
        <div className="flex gap-3">
          <button onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm hover:border-[#388bfd] hover:text-[#388bfd] transition-colors">
            <Plus size={14} />Add IOC
          </button>
          <button onClick={() => scanMutation.mutate()} disabled={scanMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#f85149] text-white text-sm font-semibold hover:opacity-90 disabled:opacity-50">
            <Play size={14} />{scanMutation.isPending ? "Scanning..." : "Run IOC Scan"}
          </button>
        </div>
      }
    >
      {showForm && (
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form); }}
          className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">IOC Type</label>
              <select value={form.ioc_type} onChange={(e) => setForm({ ...form, ioc_type: e.target.value })}
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2">
                {IOC_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs text-[#8b949e] mb-1.5">Indicator Value</label>
              <input value={form.value} onChange={(e) => setForm({ ...form, value: e.target.value })}
                placeholder="192.168.1.1 / malware.exe / abc123..."
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 font-mono focus:outline-none focus:border-[#388bfd]" required />
            </div>
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">Risk Score (0-100)</label>
              <input type="number" min={0} max={100} value={form.risk_score} onChange={(e) => setForm({ ...form, risk_score: +e.target.value })}
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2" />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs text-[#8b949e] mb-1.5">Description</label>
              <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Source, context, or notes..."
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]" />
            </div>
          </div>
          <div className="flex gap-3">
            <button type="submit" disabled={createMutation.isPending}
              className="px-4 py-2 rounded-lg bg-[#388bfd] text-white text-sm font-semibold hover:bg-[#1f6feb] disabled:opacity-50">
              {createMutation.isPending ? "Adding..." : "Add IOC"}
            </button>
            <button type="button" onClick={() => setShowForm(false)}
              className="px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm">Cancel</button>
          </div>
        </form>
      )}

      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58]">Indicators ({iocs.length})</div>
      <DataTable data={iocs} columns={iocCols} rowKey="id" emptyMessage="No IOCs yet" maxHeight="280px" />

      <div className="mt-6 mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58]">Matches ({matches.length})</div>
      <DataTable data={matches} columns={matchCols} rowKey="id" emptyMessage="Run IOC scan to find matches in evidence" />
    </PageWrapper>
  );
}
