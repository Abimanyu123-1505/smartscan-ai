import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";

export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
  mono?: boolean;
}

interface DataTableProps<T extends object> {
  data: T[];
  columns: Column<T>[];
  rowKey: keyof T;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  maxHeight?: string;
}

export default function DataTable<T extends object>({
  data,
  columns,
  rowKey,
  onRowClick,
  emptyMessage = "No data available",
  maxHeight = "60vh",
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sorted = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const av = (a as Record<string, unknown>)[sortKey];
      const bv = (b as Record<string, unknown>)[sortKey];
      const cmp = String(av ?? "").localeCompare(String(bv ?? ""), undefined, { numeric: true });
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  const toggleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <div
      className="border border-[#21262d] rounded-xl overflow-auto"
      style={{ maxHeight }}
    >
      <table className="w-full border-collapse">
        <thead className="sticky top-0 z-10 bg-[#161b22]">
          <tr>
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className={`px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-[#8b949e] border-b border-[#21262d] ${
                  col.sortable ? "cursor-pointer hover:text-[#e6edf3] select-none" : ""
                }`}
                style={{ width: col.width }}
                onClick={col.sortable ? () => toggleSort(String(col.key)) : undefined}
              >
                <div className="flex items-center gap-1.5">
                  {col.header}
                  {col.sortable && (
                    <span className="text-[#30363d]">
                      {sortKey === col.key ? (
                        sortDir === "asc" ? <ChevronUp size={12} /> : <ChevronDown size={12} />
                      ) : (
                        <ChevronDown size={12} />
                      )}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="text-center py-12 text-[#484f58] text-sm"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sorted.map((row, i) => (
              <tr
                key={String(row[rowKey])}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                className={`border-b border-[#21262d] last:border-0 transition-colors ${
                  onRowClick ? "cursor-pointer hover:bg-[rgba(56,139,253,0.05)]" : "hover:bg-[rgba(255,255,255,0.02)]"
                } ${ i % 2 === 0 ? "" : "bg-[rgba(255,255,255,0.01)]" }`}
              >
                {columns.map((col) => (
                  <td
                    key={String(col.key)}
                    className={`px-4 py-3 text-sm text-[#e6edf3] ${
                      col.mono ? "font-mono text-xs text-[#8b949e]" : ""
                    }`}
                  >
                    {col.render ? col.render(row) : String(((row as Record<string, unknown>)[String(col.key)]) ?? "")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
