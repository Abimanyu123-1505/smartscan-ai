import { useState } from "react";
import { useParams } from "react-router-dom";
import { Search as SearchIcon, Loader } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { searchApi } from "../api/client";
import type { SearchResult } from "../types";

export default function Search() {
  const { caseId } = useParams<{ caseId: string }>();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim() || !caseId) return;
    setLoading(true);
    setSearched(true);
    try {
      const data = await searchApi.search(caseId, query);
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const ARTIFACT_COLORS: Record<string, string> = {
    file: "#388bfd", process: "#f85149", registry: "#bc8cff",
    network: "#e3b341", browser: "#3fb950", memory: "#bc8cff",
  };

  return (
    <PageWrapper title="Evidence Search" subtitle="Full-text search across all extracted artifacts and evidence">
      <form onSubmit={handleSearch} className="flex gap-3 mb-6">
        <div className="flex-1 bg-[#161b22] border border-[#30363d] rounded-xl px-4 py-3 flex items-center gap-3 focus-within:border-[#388bfd] transition-colors">
          <SearchIcon size={16} className="text-[#484f58] shrink-0" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search file paths, hashes, registry keys, URLs, process names..."
            className="flex-1 bg-transparent text-[#e6edf3] text-sm outline-none placeholder:text-[#484f58]"
          />
        </div>
        <button type="submit" disabled={loading}
          className="px-5 py-3 rounded-xl bg-[#388bfd] text-white text-sm font-semibold hover:bg-[#1f6feb] disabled:opacity-50">
          {loading ? <Loader size={16} className="animate-spin" /> : "Search"}
        </button>
      </form>

      {searched && !loading && (
        <div className="text-xs text-[#484f58] mb-4">
          {results.length} result{results.length !== 1 ? "s" : ""} for "{query}"
        </div>
      )}

      <div className="space-y-2">
        {results.map((r) => (
          <div key={r.artifact_id} className="bg-[#161b22] border border-[#21262d] rounded-xl p-4 hover:border-[#30363d] transition-all">
            <div className="flex items-center gap-3 mb-2">
              <span
                className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded"
                style={{
                  color: ARTIFACT_COLORS[r.artifact_type] ?? "#8b949e",
                  background: `${ARTIFACT_COLORS[r.artifact_type] ?? "#8b949e"}15`,
                }}
              >
                {r.artifact_type}
              </span>
              <span className="font-semibold text-[#e6edf3] text-sm">{r.name}</span>
              <span className="hash-chip ml-auto">{r.artifact_id.slice(0, 8)}</span>
            </div>
            <div className="font-mono text-xs text-[#484f58] mb-1">{r.path}</div>
            {r.snippet && (
              <div className="text-xs text-[#8b949e] bg-[#0d1117] rounded-lg px-3 py-2 font-mono border-l-2 border-[#388bfd]">
                ...{r.snippet}...
              </div>
            )}
          </div>
        ))}
        {searched && !loading && results.length === 0 && (
          <div className="text-center py-16 text-[#484f58]">
            <SearchIcon size={40} className="mx-auto mb-4 opacity-20" />
            No results found for "{query}"
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
