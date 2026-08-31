import { type ReactNode } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard, Briefcase, HardDrive, Clock, Brain, Database,
  Monitor, Globe, Shield, Search, FileText, Network, Zap, Cpu, Map,
  Bot, Settings, ChevronLeft, ChevronRight, Bell, Command, AlertTriangle,
  GitBranch, Layers
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useAppStore } from "../../stores/appStore";

interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  group?: string;
  caseRequired?: boolean;
}

const TOP_NAV: NavItem[] = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/cases", label: "Cases", icon: Briefcase },
];

const CASE_NAV: NavItem[] = [
  { path: "/evidence", label: "Evidence", icon: Database, group: "Investigation" },
  { path: "/timeline", label: "Timeline", icon: Clock, group: "Investigation" },
  { path: "/search", label: "Search", icon: Search, group: "Investigation" },
  { path: "/disk", label: "Disk Forensics", icon: HardDrive, group: "Forensics" },
  { path: "/memory", label: "Memory", icon: Brain, group: "Forensics" },
  { path: "/registry", label: "Registry", icon: Layers, group: "Forensics" },
  { path: "/browser", label: "Browser", icon: Globe, group: "Forensics" },
  { path: "/network", label: "Network", icon: Network, group: "Forensics" },
  { path: "/malware", label: "Malware", icon: Shield, group: "Detection" },
  { path: "/yara", label: "YARA", icon: Zap, group: "Detection" },
  { path: "/sigma", label: "Sigma", icon: AlertTriangle, group: "Detection" },
  { path: "/ioc", label: "IOC Hunting", icon: Map, group: "Detection" },
  { path: "/mitre", label: "MITRE ATT&CK", icon: GitBranch, group: "Detection" },
  { path: "/graph", label: "Graph", icon: GitBranch, group: "Analysis" },
  { path: "/ai", label: "AI Assistant", icon: Bot, group: "Analysis" },
  { path: "/reports", label: "Reports", icon: FileText, group: "Output" },
];

const BOTTOM_NAV: NavItem[] = [
  { path: "/settings", label: "Settings", icon: Settings },
];

function NavLink({ item, collapsed, basePath = "" }: { item: NavItem; collapsed: boolean; basePath?: string }) {
  const location = useLocation();
  const fullPath = basePath + item.path;
  const isActive = location.pathname === fullPath ||
    (item.path !== "/" && location.pathname.startsWith(fullPath));

  return (
    <Link
      to={fullPath}
      title={collapsed ? item.label : undefined}
      className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-all duration-150 group relative
        ${ isActive
          ? "bg-[rgba(56,139,253,0.15)] text-[#58a6ff] font-medium"
          : "text-[#8b949e] hover:text-[#e6edf3] hover:bg-[rgba(255,255,255,0.05)]"
        }`}
    >
      <item.icon size={16} className={`shrink-0 ${ isActive ? "text-[#388bfd]" : "" }`} />
      {!collapsed && <span className="truncate">{item.label}</span>}
      {isActive && !collapsed && (
        <div className="absolute left-0 top-1 bottom-1 w-0.5 bg-[#388bfd] rounded-full" />
      )}
    </Link>
  );
}

export default function Shell({ children }: { children: ReactNode }) {
  const { caseId } = useParams<{ caseId: string }>();
  const location = useLocation();
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const setCollapsed = useAppStore((s) => s.setSidebarCollapsed);
  const setCommandPaletteOpen = useAppStore((s) => s.setCommandPaletteOpen);
  const notifications = useAppStore((s) => s.notifications);
  const unread = notifications.filter((n) => !n.read).length;
  const activeCase = useAppStore((s) => s.activeCase);

  // Determine base path for case nav
  const currentCaseId = caseId || location.pathname.match(/\/cases\/([a-z0-9]+)/)?.[1];
  const casePath = currentCaseId ? `/cases/${currentCaseId}` : null;

  // Group case nav items
  const groups = CASE_NAV.reduce((acc, item) => {
    const g = item.group || "";
    if (!acc[g]) acc[g] = [];
    acc[g].push(item);
    return acc;
  }, {} as Record<string, NavItem[]>);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 56 : 220 }}
        transition={{ duration: 0.2, ease: "easeInOut" }}
        className="flex flex-col border-r border-[#21262d] bg-[#0d1117] z-20 shrink-0"
        style={{ overflow: "hidden" }}
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-3 py-4 border-b border-[#21262d]">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-gradient-to-br from-[#388bfd] to-[#1f6feb] flex items-center justify-center">
                <Shield size={14} className="text-white" />
              </div>
              <div>
                <div className="font-display font-bold text-sm text-[#e6edf3] tracking-tight">DFIOP</div>
                <div className="text-[9px] text-[#484f58] font-mono uppercase tracking-widest">forensics platform</div>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-[#388bfd] to-[#1f6feb] flex items-center justify-center mx-auto">
              <Shield size={14} className="text-white" />
            </div>
          )}
        </div>

        {/* Nav */}
        <div className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
          {TOP_NAV.map((item) => (
            <NavLink key={item.path} item={item} collapsed={collapsed} />
          ))}

          {/* Case-scoped navigation */}
          {casePath && !collapsed && (
            <>
              <div className="px-3 pt-3 pb-1">
                <div className="text-[10px] font-semibold uppercase tracking-widest text-[#484f58]">
                  Active Case
                </div>
                <div className="text-xs text-[#58a6ff] font-mono truncate mt-0.5">
                  {activeCase?.name || currentCaseId}
                </div>
              </div>
              {Object.entries(groups).map(([group, items]) => (
                <div key={group}>
                  <div className="px-3 pt-2 pb-1">
                    <div className="text-[9px] font-semibold uppercase tracking-widest text-[#30363d]">{group}</div>
                  </div>
                  {items.map((item) => (
                    <NavLink key={item.path} item={item} collapsed={collapsed} basePath={casePath} />
                  ))}
                </div>
              ))}
            </>
          )}

          {casePath && collapsed && (
            CASE_NAV.map((item) => (
              <NavLink key={item.path} item={item} collapsed={collapsed} basePath={casePath} />
            ))
          )}
        </div>

        {/* Bottom nav */}
        <div className="border-t border-[#21262d] py-2 px-2 space-y-0.5">
          {BOTTOM_NAV.map((item) => (
            <NavLink key={item.path} item={item} collapsed={collapsed} />
          ))}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-[#484f58] hover:text-[#8b949e] hover:bg-[rgba(255,255,255,0.05)] w-full transition-all"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            {!collapsed && <span>Collapse</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="h-12 border-b border-[#21262d] bg-[#0d1117] flex items-center px-4 gap-4 shrink-0 z-10">
          {/* Search bar */}
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#161b22] border border-[#30363d] text-[#484f58] text-sm hover:border-[#388bfd] hover:text-[#8b949e] transition-all flex-1 max-w-xs"
          >
            <Search size={14} />
            <span>Search or jump to...</span>
            <kbd className="ml-auto text-[10px] bg-[#21262d] px-1.5 py-0.5 rounded font-mono">
              ⌘K
            </kbd>
          </button>

          <div className="flex-1" />

          {/* Status indicators */}
          <div className="flex items-center gap-1 text-[10px] font-mono text-[#3fb950]">
            <div className="w-1.5 h-1.5 rounded-full bg-[#3fb950] pulse-dot" />
            <span>API LIVE</span>
          </div>

          {/* Notifications */}
          <button className="relative p-1.5 rounded-md text-[#8b949e] hover:text-[#e6edf3] hover:bg-[rgba(255,255,255,0.05)] transition-all">
            <Bell size={16} />
            {unread > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-[#f85149] text-white text-[9px] flex items-center justify-center font-bold">
                {unread}
              </span>
            )}
          </button>

          {/* User avatar */}
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#388bfd] to-[#bc8cff] flex items-center justify-center text-white text-xs font-bold">
            IN
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-[#0d1117]">
          <div className="p-6 max-w-[1400px] mx-auto">
            {children}
          </div>
        </main>

        {/* Status bar */}
        <footer className="h-6 border-t border-[#21262d] bg-[#161b22] flex items-center px-4 gap-4 text-[10px] font-mono text-[#484f58] shrink-0">
          <span>DFIOP v2.0</span>
          <span>·</span>
          <span>Evidence: read-only</span>
          <span>·</span>
          <span>Chain-of-custody: active</span>
          {currentCaseId && (
            <>
              <span>·</span>
              <span className="text-[#388bfd]">CASE-{currentCaseId.toUpperCase()}</span>
            </>
          )}
          <div className="flex-1" />
          <span className="flex items-center gap-1">
            <Command size={10} />
            <span>K for command palette</span>
          </span>
        </footer>
      </div>
    </div>
  );
}
