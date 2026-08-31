import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Layers, Play, AlertTriangle, Filter } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import StatCard from "../components/shared/StatCard";
import { registryApi } from "../api/client";
import type { RegistryKey } from "../types";

const HIVES = ["", "SYSTEM", "SOFTWARE", "SAM", "SECURITY", "NTUSER.DAT", "USRCLASS.DAT"];
const CATEGORIES = ["", "run_key", "usb", "mru", "shellbag", "installed_app", "user_accounts", "timezone", "system_info", "network"];

export default function Registry() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();
  const [hive, setHive] = useState("");
  const [category, setCategory] = useState("");
  const [flaggedOnly, setFlaggedOnly] = useState(false);

  const { data: summary } = useQuery({ queryKey: ["registry-summary", caseId], queryFn: () => registryApi.summary(caseId!) });
  const { data: keys = [] } = useQuery({ queryKey: ["registry-keys", caseId, hive, category, flaggedOnly], queryFn: () => registryApi.keys(caseId!, { hive: hive || undefined, category: category || undefined, flagged_only: flaggedOnly }) });

  const parseMutation = useMutation({
    mutationFn: () => registryApi.parse(caseId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["registry-keys", caseId] }),
  });

  const columns = [
    { key: "hive", header: "Hive", render: (r: RegistryKey) => <span className="font-mono text-xs text-[#d29922]">{r.hive}</span> },
    { key: "key_path", header: "Key Path", mono: true, render: (r: RegistryKey) => <span className="font-mono text-[10px] text-[#8b949e]">{r.key_path}</span> },
    { key: "value_name", header: "Value", render: (r: RegistryKey) => <span className="font-semibold text-xs">{r.value_name}</span> },
    { key: "value_type", header: "Type", mono: true, render: (r: RegistryKey) => <span className="font-mono text-[10px] text-[#484f58]">{r.value_type}</span> },
    { key: "value_data", header: "Data", render: (r: RegistryKey) => <span className="font-mono text-xs text-[#e6edf3] truncate max-w-xs block" title={r.value_data}>{r.value_data}</span> },
    { key: "category", header: "Category", render: (r: RegistryKey) => <span className="badge badge-info">{r.category}</span> },
    { key: "flagged", header: "Status", render: (r: RegistryKey) => r.flagged ? <span className="badge badge-critical" title={r.flag_reason}>⚠ Flagged</span> : <span className="text-[#484f58] text-xs">—</span> },
  ];

  return (
    <PageWrapper
      title="Registry Analysis"
      subtitle="Windows registry hive parsing — Run keys, USB history, MRU, Shellbags"
      actions={
        <button onClick={() => parseMutation.mutate()} disabled={parseMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#58a6ff] text-[#0d1117] text-sm font-semibold hover:opacity-90 disabled:opacity-50">
          <Play size={14} />{parseMutation.isPending ? "Parsing..." : "Parse Hives"}
        </button>
      }
    >
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Total Keys" value={summary?.total ?? 0} icon={Layers} color="blue" />
        <StatCard label="Flagged" value={summary?.flagged ?? 0} icon={AlertTriangle} color="red" />
        <StatCard label="Hives" value={summary?.by_hive?.length ?? 0} icon={Filter} color="amber" />
      </div>
      <div className="flex gap-3 mb-4">
        <select value={hive} onChange={(e) => setHive(e.target.value)}
          className="bg-[#161b22] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2">
          {HIVES.map((h) => <option key={h} value={h}>{h || "All Hives"}</option>)}
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)}
          className="bg-[#161b22] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2">
          {CATEGORIES.map((c) => <option key={c} value={c}>{c || "All Categories"}</option>)}
        </select>
        <label className="flex items-center gap-2 text-sm text-[#8b949e] cursor-pointer">
          <input type="checkbox" checked={flaggedOnly} onChange={(e) => setFlaggedOnly(e.target.checked)} className="accent-[#f85149]" />
          Flagged only
        </label>
      </div>
      <DataTable data={keys} columns={columns} rowKey="id" emptyMessage="No registry keys. Parse hives to extract data." />
    </PageWrapper>
  );
}
