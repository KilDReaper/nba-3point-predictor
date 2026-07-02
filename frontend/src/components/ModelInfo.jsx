import React from "react";

function ModelInfo({ modelInfo }) {
  return (
    <div className="sports-card" style={styles.card}>
      <div style={styles.cardTitle}>Model Evaluation Parameters</div>
      {modelInfo ? (
        <div style={styles.tableContainer}>
          <table style={styles.table} className="text-mono">
            <tbody>
              <tr style={styles.tr}>
                <td style={styles.tdLabel}>Regressor Type</td>
                <td style={styles.tdValue}>XGBoost</td>
              </tr>
              <tr style={styles.tr}>
                <td style={styles.tdLabel}>Mean Abs. Error (MAE)</td>
                <td style={{ ...styles.tdValue, color: "var(--court-gold)" }}>
                  {(modelInfo.mae * 100).toFixed(2)}%
                </td>
              </tr>
              <tr style={styles.tr}>
                <td style={styles.tdLabel}>R² Score (Coeff. of Det.)</td>
                <td style={styles.tdValue}>{modelInfo.r2.toFixed(4)}</td>
              </tr>
              <tr style={styles.tr}>
                <td style={styles.tdLabel}>Training Size</td>
                <td style={styles.tdValue}>{modelInfo.training_rows} rows</td>
              </tr>
              <tr style={styles.tr}>
                <td style={styles.tdLabel}>Testing Size</td>
                <td style={styles.tdValue}>{modelInfo.test_rows || 488} rows</td>
              </tr>
              <tr style={styles.tr}>
                <td style={styles.tdLabel}>Historical Range</td>
                <td style={styles.tdValue}>{modelInfo.seasons}</td>
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        <div style={styles.fallback}>
          Failed to load model diagnostics. Ensure python backend is online.
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    padding: "20px",
    width: "100%",
  },
  cardTitle: {
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
  tdLabel: {
    padding: "10px 0",
    color: "var(--text-muted)",
    textAlign: "left",
  },
  tdValue: {
    padding: "10px 0",
    color: "var(--text-main)",
    textAlign: "right",
    fontWeight: 600,
  },
  fallback: {
    fontSize: "0.8rem",
    color: "var(--text-dark)",
    textAlign: "center",
    padding: "12px 0",
  }
};

export default ModelInfo;
