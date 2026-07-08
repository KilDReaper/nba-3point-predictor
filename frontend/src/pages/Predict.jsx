import React, { useState } from "react";
import { motion } from "framer-motion";
import api from "../services/api";
import PredictionForm from "../components/PredictionForm";
import PredictionCard from "../components/PredictionCard";

const FEATURE_LABELS = {
  fg3_pct_career_avg: "Career 3PT%",
  FG_PCT: "Overall FG%",
  fg3a_per_game: "3PA per Game",
  high_volume: "Volume Shooter",
  FT_PCT: "FT%",
  TOV: "Turnovers",
  fg3_pct_lag2: "3PT% (2 Yrs Ago)",
  MIN: "Minutes/Game",
};

const IMPORTANCES = [
  { key: "FG_PCT", val: 0.133 },
  { key: "fg3_pct_career_avg", val: 0.126 },
  { key: "fg3a_per_game", val: 0.112 },
  { key: "high_volume", val: 0.084 },
  { key: "FT_PCT", val: 0.074 },
  { key: "TOV", val: 0.074 },
  { key: "fg3_pct_lag2", val: 0.055 },
  { key: "MIN", val: 0.049 },
];

function Predict() {
  const [form, setForm] = useState({
    team: "GSW",
    fg3_pct_last_season: 0.370,
    fg3a_per_game: 6.0,
    games_played: 70,
    minutes_per_game: 32.0,
    fg_pct: 0.470,
    ft_pct: 0.850,
    usg_pct: 24.0,
    ast_per_game: 4.0,
    tov_per_game: 2.5,
    seasons_in_league: 5,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFormChange = (key, val) => {
    setForm((prev) => ({
      ...prev,
      [key]: val,
    }));
  };

  const handlePredict = () => {
    setLoading(true);
    setError("");
    setResult(null);

    api.post("/predict", form)
      .then((res) => {
        setResult(res.data);
      })
      .catch((err) => {
        console.error(err);
        setError("Forecast calculation failed. Ensure Python API is online.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={styles.container}
    >
      <div style={styles.grid}>
        {/* Left Column: Form parameters */}
        <PredictionForm
          form={form}
          onChange={handleFormChange}
          onSubmit={handlePredict}
          loading={loading}
        />

        {/* Right Column: Output Report & Feature Importances */}
        <div style={styles.rightCol}>
          <PredictionCard result={result} />

          {error && <div className="error-box" style={{ marginTop: "16px" }}>{error}</div>}

          {/* Feature Importances card */}
          <div className="sports-card" style={styles.importanceCard}>
            <div style={styles.cardHeader}>
              <h3 style={styles.sectionTitle}>Model Feature Weights</h3>
              <span style={styles.monoSub}>XGBOOST FEATURE IMPORTANCE</span>
            </div>
            <div style={styles.featList}>
              {IMPORTANCES.map((item) => (
                <div key={item.key} style={styles.featRow}>
                  <div style={styles.featName}>
                    {FEATURE_LABELS[item.key] || item.key}
                  </div>
                  <div style={styles.barBg}>
                    <div
                      style={{
                        ...styles.barFill,
                        width: `${(item.val / 0.133) * 100}%`,
                      }}
                    ></div>
                  </div>
                  <div style={styles.featVal} className="text-mono">
                    {(item.val * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

const styles = {
  container: {
    width: "100%",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "380px 1fr",
    gap: "24px",
    alignItems: "start",
  },
  rightCol: {
    display: "flex",
    flexDirection: "column",
    gap: "24px",
  },
  importanceCard: {
    padding: "20px",
    boxSizing: "border-box",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
    borderBottom: "1px solid var(--border-color)",
    paddingBottom: "10px",
  },
  sectionTitle: {
    fontFamily: "var(--heading)",
    fontSize: "1.1rem",
    color: "#fff",
  },
  monoSub: {
    fontFamily: "var(--mono)",
    fontSize: "0.68rem",
    color: "var(--text-dark)",
  },
  featList: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  featRow: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    fontSize: "0.8rem",
  },
  featName: {
    width: "150px",
    fontWeight: 500,
    color: "var(--text-muted)",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
  },
  barBg: {
    flex: 1,
    height: "6px",
    background: "#161b26",
    borderRadius: "3px",
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    background: "var(--court-gold)",
    borderRadius: "3px",
  },
  featVal: {
    width: "40px",
    textAlign: "right",
    color: "var(--text-main)",
    fontWeight: 600,
  }
};

export default Predict;
