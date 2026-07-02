import React from "react";

function PredictionCard({ result }) {
  if (!result) {
    return (
      <div className="sports-card" style={styles.card}>
        <div style={styles.title}>Prediction Report</div>
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>📊</div>
          <div style={styles.emptyText}>
            Simulate stats in the left control panel and run regression to compile output.
          </div>
        </div>
      </div>
    );
  }

  const isElite = result.predicted_fg3_pct >= 0.38;

  return (
    <div className={`sports-card ${isElite ? "made" : "primary"}`} style={styles.card}>
      <div style={styles.title}>Forecast Summary Report</div>
      
      <div style={styles.badge}>
        <div style={styles.percentage} className="text-mono">
          {result.predicted_fg3_pct_percent}%
        </div>
        <div style={styles.label}>Predicted Next Season 3PT%</div>
        <div style={styles.status}>
          SHOOTER STATUS:{" "}
          <strong style={{ color: isElite ? "var(--color-made)" : "var(--court-gold)" }}>
            {isElite ? "ELITE / SNIPER" : "STANDARD RANGE"}
          </strong>
        </div>
      </div>

      <div style={styles.tableContainer}>
        <table className="custom-table text-mono" style={styles.table}>
          <thead>
            <tr style={styles.tr}>
              <th style={styles.th}>INPUT CATEGORY</th>
              <th style={styles.thRight}>VALUE</th>
            </tr>
          </thead>
          <tbody>
            <tr style={styles.tr}>
              <td style={styles.td}>Last Season 3PT%</td>
              <td style={styles.tdRight}>
                {(result.input.fg3_pct_last_season * 100).toFixed(1)}%
              </td>
            </tr>
            <tr style={styles.tr}>
              <td style={styles.td}>Attempts / Game</td>
              <td style={styles.tdRight}>{result.input.fg3a_per_game}</td>
            </tr>
            <tr style={styles.tr}>
              <td style={styles.td}>Overall FG%</td>
              <td style={styles.tdRight}>
                {(result.input.fg_pct * 100).toFixed(1)}%
              </td>
            </tr>
            <tr style={styles.tr}>
              <td style={styles.td}>FT%</td>
              <td style={styles.tdRight}>
                {(result.input.ft_pct * 100).toFixed(1)}%
              </td>
            </tr>
            <tr style={styles.tr}>
              <td style={styles.td}>Usage Rate</td>
              <td style={styles.tdRight}>{result.input.usg_pct}%</td>
            </tr>
            <tr style={styles.tr}>
              <td style={styles.td}>Games Played</td>
              <td style={styles.tdRight}>{result.input.games_played}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

const styles = {
  card: {
    padding: "20px",
    width: "100%",
    boxSizing: "border-box",
  },
  title: {
    fontFamily: "var(--heading)",
    textTransform: "uppercase",
    letterSpacing: "0.03em",
    fontWeight: 600,
    fontSize: "1.1rem",
    color: "var(--text-main)",
    marginBottom: "16px",
    borderBottom: "1px solid var(--border-color)",
    paddingBottom: "10px",
  },
  empty: {
    height: "240px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "16px",
    color: "var(--text-dark)",
    textAlign: "center",
    padding: "20px",
  },
  emptyIcon: {
    fontSize: "2.5rem",
    opacity: 0.2,
  },
  emptyText: {
    fontSize: "0.82rem",
    maxWidth: "260px",
    lineHeight: 1.5,
  },
  badge: {
    padding: "20px",
    borderRadius: "4px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    textAlign: "center",
    marginBottom: "20px",
  },
  percentage: {
    fontWeight: 700,
    fontSize: "3.6rem",
    lineHeight: 1,
    color: "var(--court-gold)",
  },
  label: {
    fontFamily: "var(--heading)",
    fontSize: "0.8rem",
    fontWeight: 500,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    color: "var(--text-muted)",
    marginTop: "6px",
  },
  status: {
    fontFamily: "var(--heading)",
    fontSize: "0.9rem",
    fontWeight: 600,
    marginTop: "10px",
    letterSpacing: "0.02em",
    color: "var(--text-main)",
  },
  tableContainer: {
    width: "100%",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "0.8rem",
  },
  tr: {
    borderBottom: "1px solid rgba(255, 255, 255, 0.03)",
  },
  th: {
    textAlign: "left",
    padding: "8px 10px",
    fontSize: "0.68rem",
    color: "var(--text-muted)",
  },
  thRight: {
    textAlign: "right",
    padding: "8px 10px",
    fontSize: "0.68rem",
    color: "var(--text-muted)",
  },
  td: {
    padding: "8px 10px",
    color: "var(--text-muted)",
    textAlign: "left",
  },
  tdRight: {
    padding: "8px 10px",
    color: "var(--text-main)",
    textAlign: "right",
    fontWeight: 600,
  }
};

export default PredictionCard;
