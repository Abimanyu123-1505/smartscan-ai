import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Search, LayoutDashboard, Briefcase, HardDrive, Clock, Brain, Shield, Network, Bot, FileText, Zap, AlertTriangle, Map, GitBranch } from "lucide-react";

interface Command {
  id: string;
  label: string;
  description?: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  action: () => void;
  group: string;
}

export default function CommandPalette({ onClose }: { onClose: () => void }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const commands: Command[] = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, action: () => navigate("/"), group: "Navigate" },
    { id: "cases", label: "Cases", description: "View all cases", icon: Briefcase, action: () => navigate("/cases"), group: "Navigate" },
    { id: "new-case", label: "New Case", description: "Open a new investigation", icon: Briefcase, action: () => navigate("/cases"), group: "Actions" },
    { id: "settings", label: "Settings", icon: Shield, action: () => navigate("/settings"), group: "Navigate" },
  ];

  const filtered = query
    ? commands.filter(
        (c) =>
          c.label.toLowerCase().includes(query.toLowerCase()) ||
          c.description?.toLowerCase().includes(query.toLowerCase())
      )
    : commands;

  const groups = filtered.reduce((acc, cmd) => {
    if (!acc[cmd.group]) acc[cmd.group] = [];
    acc[cmd.group].push(cmd);
    return acc;
  }, {} as Record<string, Command[]>);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        transition={{ duration: 0.15 }}
        className="relative w-full max-w-lg bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-[#21262d]">
          <Search size={16} className="text-[#484f58] shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search commands, navigate, run analysis..."
            className="flex-1 bg-transparent text-[#e6edf3] text-sm outline-none placeholder:text-[#484f58]"
          />
          <kbd className="text-[10px] bg-[#21262d] text-[#484f58] px-1.5 py-0.5 rounded font-mono">ESC</kbd>
        </div>

        {/* Results */}
        <div className="max-h-96 overflow-y-auto py-2">
          {Object.entries(groups).map(([group, cmds]) => (
            <div key={group}>
              <div className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-[#484f58]">
                {group}
              </div>
              {cmds.map((cmd) => (
                <button
                  key={cmd.id}
                  onClick={() => { cmd.action(); onClose(); }}
                  className="flex items-center gap-3 w-full px-4 py-2.5 text-left hover:bg-[rgba(56,139,253,0.1)] transition-colors group"
                >
                  <div className="w-7 h-7 rounded-md bg-[#21262d] flex items-center justify-center group-hover:bg-[rgba(56,139,253,0.2)] transition-colors">
                    <cmd.icon size={14} className="text-[#8b949e] group-hover:text-[#388bfd]" />
                  </div>
                  <div>
                    <div className="text-sm text-[#e6edf3] font-medium">{cmd.label}</div>
                    {cmd.description && (
                      <div className="text-xs text-[#484f58]">{cmd.description}</div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="px-4 py-8 text-center text-[#484f58] text-sm">
              No commands found for "{query}"
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-[#21262d] flex gap-4 text-[10px] text-[#484f58] font-mono">
          <span>↑↓ Navigate</span>
          <span>↵ Select</span>
          <span>ESC Close</span>
        </div>
      </motion.div>
    </div>
  );
}
