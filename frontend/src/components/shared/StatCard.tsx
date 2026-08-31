import { type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  color?: "blue" | "red" | "green" | "amber" | "purple" | "teal";
  trend?: number;
  sublabel?: string;
}

const colorMap = {
  blue: { bg: "rgba(56,139,253,0.1)", text: "#388bfd", border: "rgba(56,139,253,0.2)" },
  red: { bg: "rgba(248,81,73,0.1)", text: "#f85149", border: "rgba(248,81,73,0.2)" },
  green: { bg: "rgba(63,185,80,0.1)", text: "#3fb950", border: "rgba(63,185,80,0.2)" },
  amber: { bg: "rgba(210,153,34,0.1)", text: "#d29922", border: "rgba(210,153,34,0.2)" },
  purple: { bg: "rgba(188,140,255,0.1)", text: "#bc8cff", border: "rgba(188,140,255,0.2)" },
  teal: { bg: "rgba(57,211,83,0.1)", text: "#39d353", border: "rgba(57,211,83,0.2)" },
};

export default function StatCard({ label, value, icon: Icon, color = "blue", trend, sublabel }: StatCardProps) {
  const c = colorMap[color];
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="bg-[#161b22] border border-[#21262d] rounded-xl p-4 flex items-start gap-4 hover:border-[#30363d] transition-all cursor-default"
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
        style={{ background: c.bg, border: `1px solid ${c.border}` }}
      >
        <Icon size={18} style={{ color: c.text }} />
      </div>
      <div className="min-w-0">
        <div className="text-[#8b949e] text-xs font-medium uppercase tracking-wider mb-1">{label}</div>
        <div className="text-2xl font-bold text-[#e6edf3] font-display" style={{ color: c.text }}>
          {typeof value === "number" ? value.toLocaleString() : value}
        </div>
        {sublabel && <div className="text-xs text-[#484f58] mt-0.5">{sublabel}</div>}
        {trend !== undefined && (
          <div className={`text-xs mt-1 ${trend >= 0 ? "text-[#3fb950]" : "text-[#f85149]"}`}>
            {trend >= 0 ? "↑" : "↓"} {Math.abs(trend)}% this week
          </div>
        )}
      </div>
    </motion.div>
  );
}
