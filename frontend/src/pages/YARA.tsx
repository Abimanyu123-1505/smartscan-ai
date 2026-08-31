import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Zap, Plus, Play, Trash2 } from "lucide-react";
import Editor from "@monaco-editor/react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import { yaraApi } from "../api/client";
import type { YARARule, YARAMatch } from "../types";

const DEFAULT_RULE = `rule SuspiciousProcess {
  meta:
    author = "analyst"
    description = "Detect suspicious process names"
  strings:
    $s1 = "mimikatz" nocase
    $s2 = "meterpreter" nocase
    $s3 = "cobaltstrike" nocase
  condition:
    any of them
}`;

export default function YARA() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [ruleText, setRuleText] = useState(DEFAULT_RULE);
  const [ruleName, setRuleName] = useState("");
  const [ruleDesc, setRuleDesc] = useState("");

  const { data: rules = [] } = useQuery({ queryKey: ["yara-rules"], queryFn: yaraApi.rules });
  const { data: matches = [] } = useQuery({ queryKey: ["yara-matches", caseId], queryFn: () => yaraApi.matches(caseId!) });

  const createMutation = useMutation({
    mutationFn: () => yaraApi.createRule({ name: ruleName, description: ruleDesc, rule_text: ruleText }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["yara-rules"] }); setShowForm(false); },
  });

  const scanMutation = useMutation({
    mutationFn: () => yaraApi.scan(caseId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["yara-matches", caseId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => yaraApi.deleteRule(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["yara-rules"] }),
  });

  const ruleCols = [
    { key: "name", header: "Rule Name", render: (r: YARARule) => <span className="font-semibold text-[#e6edf3]">{r.name}</span>, sortable: true },
    { key: "author", header: "Author" },
    { key: "enabled", header: "Status", render: (r: YARARule) => r.enabled ? <span className="badge badge-ok">Enabled</span> : <span className="badge badge-low">Disabled</span> },
    { key: "match_count", header: "Matches", render: (r: YARARule) => <span className={`font-mono font-bold ${r.match_count > 0 ? "text-[#f85149]" : "text-[#484f58]"}`}>{r.match_count}</span>, sortable: true },
    { key: "created_at", header: "Created", render: (r: YARARule) => new Date(r.created_at).toLocaleDateString() },
    { key: "actions", header: "", render: (r: YARARule) => (
      <button onClick={() => deleteMutation.mutate(r.id)} className="p-1 text-[#484f58] hover:text-[#f85149] transition-colors">
        <Trash2 size={14} />
      </button>
    )},
  ];

  const matchCols = [
    { key: "rule_id", header: "Rule", mono: true, render: (r: YARAMatch) => <span className="hash-chip">{r.rule_id.slice(0, 8)}</span> },
    { key: "file_path", header: "File", render: (r: YARAMatch) => <span className="font-mono text-xs text-[#e6edf3]">{r.file_path}</span> },
    { key: "matched_at", header: "Matched At", render: (r: YARAMatch) => new Date(r.matched_at).toLocaleString() },
  ];

  return (
    <PageWrapper
      title="YARA Scanning"
      subtitle="Write and run YARA rules against acquired evidence"
      actions={
        <div className="flex gap-3">
          <button onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm hover:border-[#d29922] hover:text-[#d29922] transition-colors">
            <Plus size={14} />New Rule
          </button>
          <button onClick={() => scanMutation.mutate()} disabled={scanMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#d29922] text-[#0d1117] text-sm font-semibold hover:opacity-90 disabled:opacity-50">
            <Play size={14} />{scanMutation.isPending ? "Scanning..." : "Run Scan"}
          </button>
        </div>
      }
    >
      {showForm && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">Rule Name</label>
              <input value={ruleName} onChange={(e) => setRuleName(e.target.value)}
                placeholder="MyYARARule"
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 font-mono" />
            </div>
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">Description</label>
              <input value={ruleDesc} onChange={(e) => setRuleDesc(e.target.value)}
                placeholder="What does this rule detect?"
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2" />
            </div>
          </div>
          <label className="block text-xs text-[#8b949e] mb-1.5">Rule Source (YARA syntax)</label>
          <div className="border border-[#30363d] rounded-lg overflow-hidden mb-4" style={{ height: 300 }}>
            <Editor
              height="300px"
              language="c"
              theme="vs-dark"
              value={ruleText}
              onChange={(v) => setRuleText(v ?? "")}
              options={{ minimap: { enabled: false }, fontSize: 13, scrollBeyondLastLine: false }}
            />
          </div>
          <div className="flex gap-3">
            <button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !ruleName}
              className="px-4 py-2 rounded-lg bg-[#d29922] text-[#0d1117] text-sm font-semibold disabled:opacity-50">
              {createMutation.isPending ? "Saving..." : "Save Rule"}
            </button>
            <button onClick={() => setShowForm(false)}
              className="px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm">Cancel</button>
          </div>
        </div>
      )}

      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58]">Rules ({rules.length})</div>
      <DataTable data={rules} columns={ruleCols} rowKey="id" maxHeight="280px" emptyMessage="No YARA rules yet" />

      <div className="mt-6 mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58]">Matches ({matches.length})</div>
      <DataTable data={matches} columns={matchCols} rowKey="id" emptyMessage="No matches. Run YARA scan against evidence." />
    </PageWrapper>
  );
}
