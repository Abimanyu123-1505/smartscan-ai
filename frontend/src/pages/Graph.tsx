import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { ReactFlow, Background, Controls, MiniMap, MarkerType, type Node, type Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { GitBranch, Play, RefreshCw } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { graphApi } from "../api/client";

const NODE_COLORS: Record<string, string> = {
  file: "#388bfd",
  process: "#f85149",
  network: "#e3b341",
  registry: "#bc8cff",
  user: "#3fb950",
  host: "#8b949e",
};

export default function Graph() {
  const { caseId } = useParams<{ caseId: string }>();
  const qc = useQueryClient();

  const { data: graphData, isLoading } = useQuery({
    queryKey: ["graph", caseId],
    queryFn: () => graphApi.get(caseId!),
  });

  const buildMutation = useMutation({
    mutationFn: () => graphApi.build(caseId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["graph", caseId] }),
  });

  const nodes: Node[] = (graphData?.nodes ?? []).map((n, i) => ({
    id: n.id,
    position: { x: (i % 8) * 200, y: Math.floor(i / 8) * 120 },
    data: { label: n.label },
    style: {
      background: `${NODE_COLORS[n.type] ?? "#8b949e"}20`,
      border: `1px solid ${NODE_COLORS[n.type] ?? "#8b949e"}60`,
      color: NODE_COLORS[n.type] ?? "#8b949e",
      fontSize: 11,
      fontFamily: "JetBrains Mono, monospace",
      padding: "6px 12px",
      borderRadius: 6,
    },
  }));

  const edges: Edge[] = (graphData?.edges ?? []).map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label,
    animated: true,
    markerEnd: { type: MarkerType.ArrowClosed, color: "#30363d" },
    style: { stroke: "#30363d" },
    labelStyle: { fill: "#484f58", fontSize: 9 },
  }));

  return (
    <PageWrapper
      title="Entity Relationship Graph"
      subtitle="Visualize relationships between artifacts, processes, network entities, and files"
      actions={
        <button onClick={() => buildMutation.mutate()} disabled={buildMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#3fb950] text-[#0d1117] text-sm font-semibold hover:opacity-90 disabled:opacity-50">
          {buildMutation.isPending ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
          {buildMutation.isPending ? "Building..." : "Build Graph"}
        </button>
      }
    >
      <div
        className="bg-[#161b22] border border-[#21262d] rounded-xl overflow-hidden"
        style={{ height: "calc(100vh - 260px)" }}
      >
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-[#484f58]">
            Loading graph...
          </div>
        ) : nodes.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-[#484f58]">
            <GitBranch size={40} className="mb-4 opacity-20" />
            <div>No graph data yet. Build the entity graph from case evidence.</div>
          </div>
        ) : (
          <ReactFlow nodes={nodes} edges={edges} fitView colorMode="dark">
            <Background color="#21262d" gap={20} />
            <Controls />
            <MiniMap
              nodeColor={(n) => NODE_COLORS[(n.data as Record<string, string>)?.type ?? ""] ?? "#484f58"}
              style={{ background: "#0d1117", border: "1px solid #21262d" }}
            />
          </ReactFlow>
        )}
      </div>
    </PageWrapper>
  );
}
