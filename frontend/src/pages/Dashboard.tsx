import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import {
  Briefcase, Database, Clock, Shield, AlertTriangle,
  HardDrive, Zap, Activity, TrendingUp, Server
} from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import StatCard from "../components/shared/StatCard";
import { dashboardApi } from "../api/client";

export default function Dashboard() {
  const { data: stats } = useQuery({ queryKey: ["dashboard", "stats"], queryFn: dashboardApi.stats });
  const { data: trend } = useQuery({ queryKey: ["dashboard", "trend"], queryFn: dashboardApi.caseTrend });
  const { data: types } = useQuery({ queryKey: ["dashboard", "types"], queryFn: dashboardApi.evidenceTypes });
  const { data: activity } = useQuery({ queryKey: ["dashboard", "activity"], queryFn: dashboardApi.recentActivity });

  const trendOption = {
    backgroundColor: "transparent",
    grid: { top: 10, right: 10, bottom: 30, left: 40 },
    xAxis: {
      type: "category",
      data: trend?.trend.map((t) => t.date.slice(5)) ?? [],
      axisLine: { lineStyle: { color: "#30363d" } },
      axisLabel: { color: "#484f58", fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value",
      axisLine: { show: false },
      axisLabel: { color: "#484f58", fontSize: 11 },
      splitLine: { lineStyle: { color: "#21262d" } },
    },
    series: [
      {
        data: trend?.trend.map((t) => t.count) ?? [],
        type: "line",
        smooth: true,
        lineStyle: { color: "#388bfd", width: 2 },
        areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(56,139,253,0.3)" }, { offset: 1, color: "rgba(56,139,253,0)" }] } },
        symbol: "none",
      },
    ],
    tooltip: { trigger: "axis", backgroundColor: "#161b22", borderColor: "#30363d", textStyle: { color: "#e6edf3" } },
  };

  const donutOption = {
    backgroundColor: "transparent",
    series: [
      {
        type: "pie",
        radius: ["55%", "80%"],
        data: types?.types.map((t, i) => ({
          name: t.type,
          value: t.count,
          itemStyle: { color: ["#388bfd", "#3fb950", "#d29922", "#f85149", "#bc8cff", "#39d353"][i % 6] },
        })) ?? [],
        label: { color: "#8b949e", fontSize: 11 },
        emphasis: { scale: true, scaleSize: 4 },
      },
    ],
    tooltip: { trigger: "item", backgroundColor: "#161b22", borderColor: "#30363d", textStyle: { color: "#e6edf3" } },
  };

  return (
    <PageWrapper title="Dashboard" subtitle="Investigation platform overview and activity summary">
      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Open Cases" value={stats?.open_cases ?? 0} icon={Briefcase} color="blue" />
        <StatCard label="Closed Cases" value={stats?.closed_cases ?? 0} icon={Briefcase} color="green" />
        <StatCard label="Evidence Items" value={stats?.total_evidence ?? 0} icon={Database} color="amber" />
        <StatCard label="Artifacts" value={stats?.total_artifacts ?? 0} icon={HardDrive} color="purple" />
        <StatCard label="Timeline Events" value={stats?.timeline_events ?? 0} icon={Clock} color="teal" />
        <StatCard label="Malware Found" value={stats?.malware_found ?? 0} icon={Shield} color="red" />
        <StatCard label="YARA Matches" value={stats?.yara_matches ?? 0} icon={Zap} color="amber" />
        <StatCard label="Sigma Alerts" value={stats?.sigma_alerts ?? 0} icon={AlertTriangle} color="red" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="lg:col-span-2 bg-[#161b22] border border-[#21262d] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp size={14} className="text-[#388bfd]" />
            <h3 className="text-sm font-semibold text-[#e6edf3]">Case Creation Trend</h3>
          </div>
          <ReactECharts option={trendOption} style={{ height: 180 }} />
        </div>
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Database size={14} className="text-[#388bfd]" />
            <h3 className="text-sm font-semibold text-[#e6edf3]">Evidence Types</h3>
          </div>
          <ReactECharts option={donutOption} style={{ height: 180 }} />
        </div>
      </div>

      {/* Recent activity */}
      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={14} className="text-[#388bfd]" />
          <h3 className="text-sm font-semibold text-[#e6edf3]">Recent Activity</h3>
        </div>
        <div className="space-y-2">
          {(activity?.activity ?? []).slice(0, 8).map((a, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b border-[#21262d] last:border-0">
              <div className="w-2 h-2 mt-1.5 rounded-full bg-[#388bfd] shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-2">
                  <span className="text-xs font-medium text-[#58a6ff]">{a.actor}</span>
                  <span className="text-xs font-semibold text-[#e6edf3]">{a.action.replace(/_/g, " ")}</span>
                  <span className="text-xs text-[#484f58] truncate">{a.detail}</span>
                </div>
              </div>
              <span className="text-[10px] text-[#484f58] font-mono shrink-0">
                {new Date(a.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))}
          {(activity?.activity ?? []).length === 0 && (
            <div className="text-center py-8 text-[#484f58] text-sm">No activity yet. Create a case to get started.</div>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}
