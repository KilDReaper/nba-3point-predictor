import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={styles.tooltip}>
        <div style={styles.tooltipTitle}>Season: {label}</div>
        <div style={{ ...styles.tooltipItem, color: "#ffffff" }}>
          <span>Actual 3PT%:</span>
          <strong className="text-mono">{payload[0].value}%</strong>
        </div>
        <div style={{ ...styles.tooltipItem, color: "var(--court-gold)" }}>
          <span>Forecasted 3PT%:</span>
          <strong className="text-mono">{payload[1].value}%</strong>
        </div>
      </div>
    );
  }
  return null;
};

function HistoryChart({ history }) {
  if (!history || history.length === 0) {
    return (
      <div style={styles.empty}>
        No historical stats available to chart.
      </div>
    );
  }

  // Format data for Recharts (multiply decimals by 100)
  const chartData = history.map((hh) => ({
    season: hh.season,
    Actual: parseFloat((hh.actual_fg3_pct * 100).toFixed(1)),
    Predicted: parseFloat((hh.predicted_fg3_pct * 100).toFixed(1)),
  }));

  return (
    <div style={styles.container}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
          <XAxis
            dataKey="season"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            stroke="rgba(255, 255, 255, 0.1)"
          />
          <YAxis
            domain={["auto", "auto"]}
            tickFormatter={(v) => v + "%"}
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            stroke="rgba(255, 255, 255, 0.1)"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            wrapperStyle={{ fontSize: "0.85rem", fontFamily: "'Outfit', sans-serif" }}
          />
          <Line
            type="monotone"
            name="Actual 3PT%"
            dataKey="Actual"
            stroke="#ffffff"
            strokeWidth={2.5}
            dot={{ r: 4, strokeWidth: 2 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            name="Model Prediction"
            dataKey="Predicted"
            stroke="var(--court-gold)"
            strokeWidth={2.5}
            strokeDasharray="5 4"
            dot={{ r: 4, fill: "var(--bg-slate)" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

const styles = {
  container: {
    width: "100%",
    height: "300px",
    marginTop: "16px",
  },
  empty: {
    height: "300px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "var(--text-dark)",
  },
  tooltip: {
    background: "var(--bg-slate)",
    border: "1px solid var(--glass-border)",
    padding: "12px",
    borderRadius: "8px",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.4)",
    boxSizing: "border-box",
  },
  tooltipTitle: {
    fontWeight: 700,
    fontSize: "0.85rem",
    marginBottom: "6px",
    color: "var(--text-main)",
  },
  tooltipItem: {
    fontSize: "0.8rem",
    marginTop: "4px",
    display: "flex",
    gap: "12px",
    justifyContent: "space-between",
  },
};

export default HistoryChart;
