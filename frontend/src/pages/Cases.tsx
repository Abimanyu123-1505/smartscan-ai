import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Briefcase, ChevronRight, Clock, AlertTriangle, Shield } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { casesApi } from "../api/client";
import type { Case } from "../types";

const PRIORITY_COLORS: Record<string, string> = {
  critical: "#f85149", high: "#d29922", medium: "#388bfd", low: "#3fb950"
};
const STATUS_COLORS: Record<string, string> = {
  open: "#388bfd", active: "#3fb950", closed: "#484f58", archived: "#484f58"
};

export default function Cases() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", investigator: "", priority: "medium", incident_type: "" });

  const { data: cases = [], isLoading } = useQuery({ queryKey: ["cases"], queryFn: casesApi.list });

  const createMutation = useMutation({
    mutationFn: (payload: typeof form) => casesApi.create(payload as Partial<import("../types").Case>),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["cases"] });
      setShowForm(false);
      setForm({ name: "", description: "", investigator: "", priority: "medium", incident_type: "" });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    createMutation.mutate(form);
  };

  return (
    <PageWrapper
      title="Case Docket"
      subtitle="Manage investigations. Each case maintains an isolated evidence store and chain-of-custody log."
      actions={
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#388bfd] text-white text-sm font-semibold hover:bg-[#1f6feb] transition-colors"
        >
          <Plus size={16} />
          New Case
        </button>
      }
    >
      {/* Create form */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <form
              onSubmit={handleSubmit}
              className="bg-[#161b22] border border-[#30363d] rounded-xl p-5 mb-6"
            >
              <h2 className="text-sm font-semibold text-[#e6edf3] mb-4">Open New Investigation</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-xs text-[#8b949e] mb-1.5 font-medium">Case Name *</label>
                  <input
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="e.g. Ransomware Incident — Finance Workstation"
                    className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-[#8b949e] mb-1.5 font-medium">Investigator</label>
                  <input
                    value={form.investigator}
                    onChange={(e) => setForm({ ...form, investigator: e.target.value })}
                    placeholder="Lead investigator name"
                    className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[#8b949e] mb-1.5 font-medium">Priority</label>
                  <select
                    value={form.priority}
                    onChange={(e) => setForm({ ...form, priority: e.target.value })}
                    className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-[#8b949e] mb-1.5 font-medium">Incident Type</label>
                  <select
                    value={form.incident_type}
                    onChange={(e) => setForm({ ...form, incident_type: e.target.value })}
                    className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd]"
                  >
                    <option value="">Select type...</option>
                    <option value="malware">Malware</option>
                    <option value="ransomware">Ransomware</option>
                    <option value="data_breach">Data Breach</option>
                    <option value="insider">Insider Threat</option>
                    <option value="phishing">Phishing</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div className="mb-4">
                <label className="block text-xs text-[#8b949e] mb-1.5 font-medium">Description</label>
                <textarea
                  rows={2}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Describe the investigation context and initial findings..."
                  className="w-full bg-[#0d1117] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#388bfd] resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-4 py-2 rounded-lg bg-[#388bfd] text-white text-sm font-semibold hover:bg-[#1f6feb] disabled:opacity-50 transition-colors"
                >
                  {createMutation.isPending ? "Creating..." : "Create Case"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 rounded-lg border border-[#30363d] text-[#8b949e] text-sm hover:border-[#484f58] transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cases list */}
      {isLoading ? (
        <div className="text-center py-16 text-[#484f58]">Loading cases...</div>
      ) : cases.length === 0 ? (
        <div className="text-center py-20">
          <Briefcase size={40} className="mx-auto text-[#30363d] mb-4" />
          <div className="text-[#484f58]">No cases yet. Open your first investigation.</div>
        </div>
      ) : (
        <div className="space-y-2">
          {cases.map((c: Case) => (
            <motion.div key={c.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Link
                to={`/cases/${c.id}`}
                className="flex items-center gap-4 p-4 bg-[#161b22] border border-[#21262d] rounded-xl hover:border-[#30363d] hover:bg-[#1c2128] transition-all group"
              >
                <div
                  className="w-2 h-10 rounded-full shrink-0"
                  style={{ background: PRIORITY_COLORS[c.priority] ?? "#388bfd" }}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-semibold text-[#e6edf3]">{c.name}</span>
                    <span className="font-mono text-[10px] text-[#d29922] bg-[rgba(210,153,34,0.1)] px-2 py-0.5 rounded">
                      CASE-{c.id.toUpperCase()}
                    </span>
                    <span
                      className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded"
                      style={{
                        color: STATUS_COLORS[c.status],
                        background: `${STATUS_COLORS[c.status]}20`,
                      }}
                    >
                      {c.status}
                    </span>
                  </div>
                  {c.description && (
                    <p className="text-xs text-[#8b949e] truncate">{c.description}</p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  <div className="text-xs text-[#8b949e] mb-1">{c.investigator || "Unassigned"}</div>
                  <div className="flex items-center gap-1 text-[10px] text-[#484f58] font-mono">
                    <Clock size={10} />
                    {new Date(c.created_at).toLocaleDateString()}
                  </div>
                </div>
                <ChevronRight size={16} className="text-[#30363d] group-hover:text-[#388bfd] transition-colors shrink-0" />
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
