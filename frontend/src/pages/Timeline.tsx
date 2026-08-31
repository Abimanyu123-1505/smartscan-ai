import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Clock, ChevronDown, ChevronUp, Filter } from "lucide-react";
import { useState } from "react";
import PageWrapper from "../components/shared/PageWrapper";
import SeverityBadge from "../components/shared/SeverityBadge";
import { timelineApi } from "../api/client";
import type { TimelineEvent } from "../types";

const SOURCES = ["", "filesystem", "registry", "prefetch", "evtx", "browser", "memory", "network", "mft"];

export default function Timeline() {
  const { caseId } = useParams<{ caseId: string }>();
  const [sourceFilter, setSourceFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["timeline", caseId],
    queryFn: () => timelineApi.list(caseId!),
  });

  const filtered = events.filter((e) => {
    if (sourceFilter && e.source_type !== sourceFilter) return false;
    if (severityFilter && e.severity !== severityFilter) return false;
    return true;
  });

  const sorted = [...filtered].sort((a, b) =>
    new Date(a.event_ts).getTime() - new Date(b.event_ts).getTime()
  );

  const toggle = (id: string) => {
    const next = new Set(expanded);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpanded(next);
  };

  const severityColors: Record<string, string> = {
    critical: "#f85149",
    high: "#d29922",
    medium: "#388bfd",
    low: "#3fb950",
    info: "#8b949e",
  };

  return (
    <PageWrapper title="Timeline" subtitle="Unified, chronological timeline of forensic events across all artifact sources">
      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}
          className="bg-[#161b22] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2">
          {SOURCES.map((s) => <option key={s} value={s}>{s || "All Sources"}</option>)}
        </select>
        <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-[#161b22] border border-[#30363d] text-[#e6edf3] text-sm rounded-lg px-3 py-2">
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="info">Info</option>
        </select>
        <div className="text-xs text-[#484f58] flex items-center gap-2">
          <Clock size={12} />{sorted.length} events
        </div>
      </div>

      {/* Timeline */}
      {isLoading ? (
        <div className="text-center py-12 text-[#484f58]">Loading timeline...</div>
      ) : sorted.length === 0 ? (
        <div className="text-center py-16 text-[#484f58]">
          <Clock size={40} className="mx-auto mb-4 opacity-20" />
          No events in timeline yet.
        </div>
      ) : (
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-[18px] top-0 bottom-0 w-px bg-[#21262d]" />

          <div className="space-y-1">
            {sorted.map((event, i) => {
              const isOpen = expanded.has(event.id);
              const color = severityColors[event.severity] ?? "#8b949e";
              const prevDate = i > 0 ? new Date(sorted[i - 1].event_ts).toLocaleDateString() : null;
              const thisDate = new Date(event.event_ts).toLocaleDateString();
              return (
                <div key={event.id}>
                  {thisDate !== prevDate && (
                    <div className="ml-10 my-4 flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-[#30363d]" />
                      <span className="text-xs font-semibold text-[#484f58] font-mono">{thisDate}</span>
                    </div>
                  )}
                  <div
                    className="flex gap-4 ml-1 cursor-pointer group"
                    onClick={() => toggle(event.id)}
                  >
                    {/* Dot */}
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 relative z-10 transition-all"
                      style={{ background: `${color}15`, border: `2px solid ${color}40` }}
                    >
                      <div className="w-2 h-2 rounded-full" style={{ background: color }} />
                    </div>

                    {/* Content */}
                    <div className="flex-1 bg-[#161b22] border border-[#21262d] rounded-xl p-3 mb-2 group-hover:border-[#30363d] transition-all">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-3 min-w-0">
                          <SeverityBadge severity={event.severity} />
                          <span className="text-xs font-mono text-[#484f58]">{event.source_type}</span>
                          {event.mitre_technique && (
                            <span className="font-mono text-[10px] text-[#bc8cff] bg-[rgba(188,140,255,0.1)] px-2 py-0.5 rounded">
                              {event.mitre_technique}
                            </span>
                          )}
                          <span className="text-sm text-[#e6edf3] truncate">{event.summary}</span>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] font-mono text-[#484f58]">
                            {new Date(event.event_ts).toLocaleTimeString()}
                          </span>
                          {isOpen ? <ChevronUp size={12} className="text-[#484f58]" /> : <ChevronDown size={12} className="text-[#484f58]" />}
                        </div>
                      </div>
                      {isOpen && (
                        <div className="mt-3 pt-3 border-t border-[#21262d] grid grid-cols-2 gap-2 text-xs">
                          <div><span className="text-[#484f58]">Event Type:</span> <span className="font-mono text-[#8b949e]">{event.event_type}</span></div>
                          <div><span className="text-[#484f58]">Artifact ID:</span> <span className="font-mono text-[#8b949e]">{event.artifact_id}</span></div>
                          <div><span className="text-[#484f58]">Timestamp:</span> <span className="font-mono text-[#8b949e]">{event.event_ts}</span></div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </PageWrapper>
  );
}
