import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Plus, Play, CheckCircle } from "lucide-react";
import Editor from "@monaco-editor/react";
import PageWrapper from "../components/shared/PageWrapper";
import DataTable from "../components/shared/DataTable";
import SeverityBadge from "../components/shared/SeverityBadge";
import { sigmaApi } from "../api/client";
import type { SigmaRule, SigmaRuleCreate, SigmaAlert } from "../types";

const DEFAULT_SIGMA = `title: Suspicious PowerShell
status: test
description: Detect suspicious PowerShell execution
logsource:
  product: windows
  service: powershell
detection:
  keywords:
    - 'EncodedCommand'
    - 'IEX'
    - 'Invoke-Expression'
  condition: keywords
level: high
tags:
  - attack.execution
  - attack.t1059.001`;

export default function Sigma() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [ruleYaml, setRuleYaml] = useState(DEFAULT_SIGMA);
  const [ruleName, setRuleName] = useState("");
  const [severity, setSeverity] = useState("medium");
  const [mitre, setMitre] = useState("");

  const { data: rules = [] } = useQuery({ queryKey: ["sigma-rules"], queryFn: sigmaApi.rules });
  const { data: alerts = [] } = useQuery({ queryKey: ["sigma-alerts", caseId], queryFn: () => sigmaApi.alerts(caseId!) });

  const createMutation = useMutation({
    mutationFn: () => sigmaApi.createRule({ name: ruleName, rule_yaml: ruleYaml, severity, mitre_technique: mitre } as SigmaRuleCreate),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["sigma-rules"] }); setShowForm(false); },
  });

  const runMutation = useMutation({
    mutationFn: () => sigmaApi.run(caseId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sigma-alerts", caseId] }),
  });

  const ackMutation = useMutation({
    mutationFn: (alertId: string) => sigmaApi.acknowledge(caseId!, alertId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sigma-alerts", caseId] }),
  });

  const ruleCols = [
    { key: "name", header: "Rule", render: (r: SigmaRule) => <span className="font-semibold">{r.name}</span> },
    { key: "severity", header: "Severity", render: (r: SigmaRule) => <SeverityBadge severity={r.severity} /> },
    { key: "mitre_technique", header: "MITRE", render: (r: SigmaRule) => r.mitre_technique ? <span className="font-mono text-[10px] text-[#bc8cff]">{r.mitre_technique}</span> : <span className="text-[#484f58]">—</span> },
    { key: "enabled", header: "Status", render: (r: SigmaRule) => r.enabled ? <span className="badge badge-ok">Enabled</span> : <span className="badge badge-low">Disabled</span> },
  ];

  const alertCols = [
    { key: "severity", header: "Severity", render: (r: SigmaAlert) => <SeverityBadge severity={r.severity} /> },
    { key: "title", header: "Alert", render: (r: SigmaAlert) => <span className="font-semibold text-[#e6edf3]">{r.title}</span> },
    { key: "description", header: "Description", render: (r: SigmaAlert) => <span className="text-xs text-[#8b949e]">{r.description}</span> },
    { key: "mitre_technique", header: "MITRE", render: (r: SigmaAlert) => r.mitre_technique ? <span className="font-mono text-[10px] text-[#bc8cff]">{r.mitre_technique}</span> : <span>—</span> },
    { key: "detected_at", header: "Detected", render: (r: SigmaAlert) => new Date(r.detected_at).toLocaleString() },
    { key: "ack", header: "Ack", render: (r: SigmaAlert) => r.acknowledged ? (
      <span className="badge badge-ok">Acknowledged</span>
    ) : (
      <button onClick={() => ackMutation.mutate(r.id)} className="flex items-center gap-1 text-xs text-[#3fb950] hover:underline">
        <CheckCircle size={12} />Acknowledge
      </button>
    )},
  ];

  return (
    <PageWrapper
      title="Sigma Detection"
      subtitle="Run Sigma rules against event logs to surface attacker behaviors"
      actions={
        <div className="flex gap-3">
          <button onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm hover:border-[#e3b341] hover:text-[#e3b341]">
            <Plus size={14} />New Rule
          </button>
          <button onClick={() => runMutation.mutate()} disabled={runMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#e3b341] text-[#0d1117] text-sm font-semibold hover:opacity-90 disabled:opacity-50">
            <Play size={14} />{runMutation.isPending ? "Running..." : "Run Detection"}
          </button>
        </div>
      }
    >
      {showForm && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6">
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">Rule Name</label>
              <input value={ruleName} onChange={(e) => setRuleName(e.target.value)}
                placeholder="SuspiciousPowerShell"
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">Severity</label>
              <select value={severity} onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2">
                <option value="low">Low</option><option value="medium">Medium</option>
                <option value="high">High</option><option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-[#8b949e] mb-1.5">MITRE Technique</label>
              <input value={mitre} onChange={(e) => setMitre(e.target.value)} placeholder="T1059.001"
                className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 font-mono" />
            </div>
          </div>
          <div className="border border-[#30363d] rounded-lg overflow-hidden mb-4" style={{ height: 260 }}>
            <Editor height="260px" language="yaml" theme="vs-dark" value={ruleYaml} onChange={(v) => setRuleYaml(v ?? "")}
              options={{ minimap: { enabled: false }, fontSize: 13 }} />
          </div>
          <div className="flex gap-3">
            <button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !ruleName}
              className="px-4 py-2 rounded-lg bg-[#e3b341] text-[#0d1117] text-sm font-semibold disabled:opacity-50">
              {createMutation.isPending ? "Saving..." : "Save Rule"}
            </button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm">Cancel</button>
          </div>
        </div>
      )}

      <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58]">Rules ({rules.length})</div>
      <DataTable data={rules} columns={ruleCols} rowKey="id" maxHeight="260px" emptyMessage="No Sigma rules" />

      <div className="mt-6 mb-2 text-xs font-semibold uppercase tracking-wider text-[#484f58]">Alerts ({alerts.length})</div>
      <DataTable data={alerts} columns={alertCols} rowKey="id" emptyMessage="No alerts. Run detection to surface matches." />
    </PageWrapper>
  );
}
