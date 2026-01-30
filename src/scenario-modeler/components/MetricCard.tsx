/**
 * Metric display card for scenario summary.
 * Ported from modelcontextprotocol/ext-apps scenario-modeler-server.
 */

interface MetricCardProps {
  label: string;
  value: string;
  variant?: "default" | "positive" | "negative";
}

export function MetricCard({
  label,
  value,
  variant = "default",
}: MetricCardProps) {
  return (
    <div className={`metric-card metric-card--${variant}`}>
      <span className="metric-value">{value}</span>
      <span className="metric-label">{label}</span>
    </div>
  );
}
