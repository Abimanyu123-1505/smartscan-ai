export type Severity = "critical" | "high" | "medium" | "low" | "info" | "ok";

export default function SeverityBadge({ severity }: { severity: string }) {
  const s = (severity || "info").toLowerCase() as Severity;
  return <span className={`badge badge-${s}`}>{s}</span>;
}
