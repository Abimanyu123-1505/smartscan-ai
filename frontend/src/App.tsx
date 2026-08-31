import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { useEffect } from "react";
import Shell from "./components/layout/Shell";
import CommandPalette from "./components/layout/CommandPalette";
import { useAppStore } from "./stores/appStore";

// Pages
import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import CaseDetail from "./pages/CaseDetail";
import EvidenceExplorer from "./pages/EvidenceExplorer";
import Timeline from "./pages/Timeline";
import Memory from "./pages/Memory";
import Disk from "./pages/Disk";
import Registry from "./pages/Registry";
import Browser from "./pages/Browser";
import Network from "./pages/Network";
import IOC from "./pages/IOC";
import YARA from "./pages/YARA";
import Sigma from "./pages/Sigma";
import Malware from "./pages/Malware";
import MITRE from "./pages/MITRE";
import Graph from "./pages/Graph";
import Search from "./pages/Search";
import Reports from "./pages/Reports";
import AIAssistant from "./pages/AIAssistant";
import Settings from "./pages/Settings";

export default function App() {
  const location = useLocation();
  const commandPaletteOpen = useAppStore((s) => s.commandPaletteOpen);
  const setCommandPaletteOpen = useAppStore((s) => s.setCommandPaletteOpen);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
      if (e.key === "Escape") setCommandPaletteOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [setCommandPaletteOpen]);

  return (
    <>
      <Shell>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cases" element={<Cases />} />
            <Route path="/cases/:caseId" element={<CaseDetail />} />
            <Route path="/cases/:caseId/evidence" element={<EvidenceExplorer />} />
            <Route path="/cases/:caseId/timeline" element={<Timeline />} />
            <Route path="/cases/:caseId/memory" element={<Memory />} />
            <Route path="/cases/:caseId/disk" element={<Disk />} />
            <Route path="/cases/:caseId/registry" element={<Registry />} />
            <Route path="/cases/:caseId/browser" element={<Browser />} />
            <Route path="/cases/:caseId/network" element={<Network />} />
            <Route path="/cases/:caseId/ioc" element={<IOC />} />
            <Route path="/cases/:caseId/yara" element={<YARA />} />
            <Route path="/cases/:caseId/sigma" element={<Sigma />} />
            <Route path="/cases/:caseId/malware" element={<Malware />} />
            <Route path="/cases/:caseId/mitre" element={<MITRE />} />
            <Route path="/cases/:caseId/graph" element={<Graph />} />
            <Route path="/cases/:caseId/search" element={<Search />} />
            <Route path="/cases/:caseId/reports" element={<Reports />} />
            <Route path="/cases/:caseId/ai" element={<AIAssistant />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </AnimatePresence>
      </Shell>
      {commandPaletteOpen && <CommandPalette onClose={() => setCommandPaletteOpen(false)} />}
    </>
  );
}
