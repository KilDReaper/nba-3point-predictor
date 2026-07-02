import React from "react";

function Hero({ modelInfo }) {
  const maePercent = modelInfo ? (modelInfo.mae * 100).toFixed(2) + "%" : "2.76%";
  const r2Value = modelInfo ? modelInfo.r2.toFixed(3) : "0.303";
  const rows = modelInfo ? modelInfo.training_rows.toLocaleString() : "1,222";
  const type = modelInfo ? modelInfo.model_type : "XGBoost Regressor";

  return (
    <div style={styles.heroStrip}>
      <div className="sports-card primary" style={styles.heroCard}>
        <div style={styles.heroLabel}>MODEL CONFIG</div>
        <div style={styles.heroValue}>{type}</div>
        <div style={styles.heroSub}>GRADIENT BOOSTED TREES</div>
      </div>
      <div className="sports-card blue" style={styles.heroCard}>
        <div style={styles.heroLabel}>MEAN ABS. ERROR</div>
        <div style={{ ...styles.heroValue, color: "var(--accent-blue)" }}>{maePercent}</div>
        <div style={styles.heroSub}>AVERAGE FORECAST DEVIATION</div>
      </div>
      <div className="sports-card made" style={styles.heroCard}>
        <div style={styles.heroLabel}>COEFF. OF DET. (R²)</div>
        <div style={{ ...styles.heroValue, color: "var(--color-made)" }}>{r2Value}</div>
        <div style={styles.heroSub}>MODEL GOODNESS OF FIT</div>
      </div>
      <div className="sports-card" style={styles.heroCard}>
        <div style={styles.heroLabel}>DATASET DEPTH</div>
        <div style={styles.heroValue}>{rows}</div>
        <div style={styles.heroSub}>HISTORICAL PLAYER SEASONS</div>
      </div>
    </div>
  );
}

const styles = {
  heroStrip: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "16px",
    marginBottom: "32px",
    width: "100%",
  },
  heroCard: {
    padding: "16px 20px",
    boxSizing: "border-box",
  },
  heroLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.78rem",
    fontWeight: 600,
    letterSpacing: "0.05em",
    color: "var(--text-muted)",
    marginBottom: "6px",
  },
  heroValue: {
    fontFamily: "var(--heading)",
    fontSize: "1.6rem",
    fontWeight: 700,
    color: "var(--text-main)",
    lineHeight: 1.1,
  },
  heroSub: {
    fontFamily: "var(--mono)",
    fontSize: "0.68rem",
    color: "var(--text-dark)",
    marginTop: "6px",
    letterSpacing: "-0.01em",
  }
};

export default Hero;
