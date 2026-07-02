import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import api from "../services/api";
import PlayerSearch from "../components/PlayerSearch";
import HistoryChart from "../components/HistoryChart";
import ModelInfo from "../components/ModelInfo";

function Player() {
  const [playerData, setPlayerData] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Load model info
    api.get("/model-info")
      .then((res) => setModelInfo(res.data))
      .catch((err) => console.error("Error loading model info:", err));
  }, []);

  const handleSelectPlayer = (name) => {
    setLoading(true);
    setError("");
    setPlayerData(null);

    api.get(`/player/${encodeURIComponent(name)}`)
      .then((res) => {
        setPlayerData(res.data);
      })
      .catch((err) => {
        console.error(err);
        setError(err.response?.data?.detail || "Player statistical profile not found");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const isElite = playerData && playerData.history.length > 0 && 
    playerData.history[playerData.history.length - 1].predicted_fg3_pct >= 0.38;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={styles.container}
    >
      {/* Top Search Banner spanning full width */}
      <div className="sports-card" style={styles.searchCard}>
        <div style={styles.cardHeader}>
          <h2 style={styles.cardTitle}>Statistical Profile Lookup</h2>
          {playerData && (
            <span style={styles.playerTitleBadge}>{playerData.player}</span>
          )}
        </div>
        <div style={styles.searchWrapper}>
          <PlayerSearch onSelectPlayer={handleSelectPlayer} />
        </div>
        {loading && (
          <div style={styles.loader}>
            <span className="spinner"></span>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginLeft: 8 }}>
              Retrieving historical metrics...
            </span>
          </div>
        )}
        {error && <div className="error-box" style={{ marginTop: "12px" }}>{error}</div>}
      </div>

      {/* Grid below search banner */}
      {!playerData ? (
        <div className="sports-card" style={styles.emptyCard}>
          <div className="empty-state">
            <div className="empty-icon" style={{ fontSize: "3rem", opacity: 0.15, marginBottom: 12 }}>🏀</div>
            <div className="empty-text" style={{ fontSize: "0.9rem", color: "var(--text-muted)", maxWidth: 320, margin: "0 auto", lineHeight: 1.5 }}>
              Use the search bar above to look up an active NBA player and load their historical shooting stats.
            </div>
          </div>
        </div>
      ) : (
        <div style={styles.grid}>
          {/* Left Column: Historical Table (Primary data) */}
          <div className="sports-card" style={styles.tableCard}>
            <div style={styles.cardHeader}>
              <h3 style={styles.sectionTitle}>Season Log History</h3>
              <span style={styles.seasonsCount}>{playerData.seasons} Seasons</span>
            </div>
            <div className="table-container" style={{ marginTop: 0 }}>
              <table className="custom-table" style={styles.table}>
                <thead>
                  <tr style={styles.tr}>
                    <th style={styles.th}>Season</th>
                    <th style={styles.th}>Actual %</th>
                    <th style={styles.th}>Model Pred.</th>
                    <th style={styles.th}>Diff</th>
                    <th style={styles.th}>3PA/G</th>
                    <th style={styles.th}>GP</th>
                  </tr>
                </thead>
                <tbody className="text-mono" style={styles.tbody}>
                  {playerData.history.slice().reverse().map((hh) => {
                    const diff = hh.predicted_fg3_pct - hh.actual_fg3_pct;
                    return (
                      <tr key={hh.season} style={styles.tr}>
                        <td style={styles.td}>{hh.season}</td>
                        <td style={styles.td}>{(hh.actual_fg3_pct * 100).toFixed(1)}%</td>
                        <td style={{ ...styles.td, color: "var(--court-gold)", fontWeight: 600 }}>
                          {(hh.predicted_fg3_pct * 100).toFixed(1)}%
                        </td>
                        <td style={styles.td} className={diff >= 0 ? "diff-positive" : "diff-negative"}>
                          {diff >= 0 ? "+" : ""}
                          {(diff * 100).toFixed(1)}%
                        </td>
                        <td style={styles.td}>{hh.fg3a_per_game}</td>
                        <td style={styles.td}>{hh.games_played}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Column: Charts & Metrics */}
          <div style={styles.rightColumn}>
            {/* Outcome panel */}
            <div className={`sports-card ${isElite ? "made" : "primary"}`} style={styles.summaryCard}>
              <div style={styles.summaryRow}>
                <div>
                  <div style={styles.summaryValue} className="text-mono">
                    {(playerData.history[playerData.history.length - 1].predicted_fg3_pct * 100).toFixed(1)}%
                  </div>
                  <div style={styles.summaryLabel}>LATEST XGBOOST SEASON REGRESSION</div>
                </div>
                <div style={styles.summaryRight}>
                  <div style={styles.summaryPlayer}>{playerData.player}</div>
                  <div style={styles.summaryStatus}>
                    STATUS: <span style={{ color: isElite ? "var(--color-made)" : "var(--court-gold)", fontWeight: "bold" }}>
                      {isElite ? "ELITE RANGE" : "STANDARD RANGE"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recharts graph panel */}
            <div className="sports-card" style={styles.chartCard}>
              <div style={styles.cardHeader}>
                <h3 style={styles.sectionTitle}>Regression vs Reality Curve</h3>
              </div>
              <HistoryChart history={playerData.history} />
            </div>

            {/* Model Info block */}
            <ModelInfo modelInfo={modelInfo} />
          </div>
        </div>
      )}
    </motion.div>
  );
}

const styles = {
  container: {
    width: "100%",
  },
  searchCard: {
    padding: "20px",
    width: "100%",
    marginBottom: "24px",
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
  cardTitle: {
    fontFamily: "var(--heading)",
    fontSize: "1.2rem",
    fontWeight: 600,
    color: "#fff",
  },
  playerTitleBadge: {
    fontFamily: "var(--heading)",
    fontSize: "1rem",
    color: "var(--court-gold)",
    background: "rgba(255, 149, 0, 0.08)",
    border: "1px solid var(--court-lines)",
    padding: "2px 10px",
    borderRadius: "2px",
  },
  searchWrapper: {
    width: "100%",
  },
  loader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "16px 0 0",
  },
  emptyCard: {
    width: "100%",
    padding: "64px 32px",
    boxSizing: "border-box",
    textAlign: "center",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1.2fr 1fr",
    gap: "24px",
    alignItems: "start",
  },
  tableCard: {
    padding: "20px",
    boxSizing: "border-box",
  },
  sectionTitle: {
    fontFamily: "var(--heading)",
    fontSize: "1.1rem",
    color: "#fff",
  },
  seasonsCount: {
    fontSize: "0.75rem",
    fontFamily: "var(--mono)",
    color: "var(--text-muted)",
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
    padding: "10px 12px",
    fontSize: "0.7rem",
    color: "var(--text-muted)",
  },
  tbody: {
    fontSize: "0.8rem",
  },
  td: {
    padding: "10px 12px",
    borderBottom: "1px solid rgba(255, 255, 255, 0.02)",
  },
  rightColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "24px",
  },
  summaryCard: {
    padding: "20px",
    boxSizing: "border-box",
  },
  summaryRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "16px",
  },
  summaryValue: {
    fontSize: "2.4rem",
    fontWeight: 700,
    color: "var(--court-gold)",
    lineHeight: 1,
  },
  summaryLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.75rem",
    letterSpacing: "0.05em",
    color: "var(--text-muted)",
    marginTop: "4px",
  },
  summaryRight: {
    textAlign: "right",
  },
  summaryPlayer: {
    fontFamily: "var(--heading)",
    fontSize: "1.2rem",
    color: "#fff",
    lineHeight: 1.1,
  },
  summaryStatus: {
    fontSize: "0.75rem",
    color: "var(--text-muted)",
    marginTop: "4px",
  },
  chartCard: {
    padding: "20px",
    boxSizing: "border-box",
  }
};

export default Player;
