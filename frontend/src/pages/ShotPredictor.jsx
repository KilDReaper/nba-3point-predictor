import React, { useState } from "react";
import { motion } from "framer-motion";
import api from "../services/api";
import { FaBasketballBall } from "react-icons/fa";

const PLAYER_OPTIONS = ["Stephen Curry", "Klay Thompson", "Damian Lillard", "James Harden"];

// Helper: Map click to NBA court space coordinate & determine Shot Zone
const calculateShotDetails = (svgX, svgY) => {
  // SVG Y is from 0 to 470. Basketball Hoop is at Y = 90 (which maps to Y = 0 in NBA coords).
  // Baseline is at Y = 50 (which maps to Y = -4.0 feet in NBA coords).
  // SVG X is from 0 to 500. Hoop is centered at X = 250 (which maps to X = 0 in NBA coords).
  // 1 foot = 10 SVG units.
  const locationX = (svgX - 250) / 10;
  const locationY = (svgY - 90) / 10;
  const shotDistance = Math.sqrt(locationX * locationX + locationY * locationY);

  // Determine basic shot zone
  let shotZone = "Above the Break 3";
  if (locationY <= 7.8 && Math.abs(locationX) >= 22.0) {
    shotZone = locationX < 0 ? "Left Corner 3" : "Right Corner 3";
  } else if (shotDistance < 8.0) {
    shotZone = "Restricted Area";
  } else if (shotDistance < 16.0) {
    shotZone = "In The Paint (Non-RA)";
  } else if (shotDistance < 22.0) {
    shotZone = "Mid-Range";
  }

  return {
    locationX: parseFloat(locationX.toFixed(2)),
    locationY: parseFloat(locationY.toFixed(2)),
    shotDistance: parseFloat(shotDistance.toFixed(2)),
    shotZone,
  };
};

function ShotPredictor() {
  const [selectedPlayer, setSelectedPlayer] = useState(PLAYER_OPTIONS[0]);
  const [clickCoords, setClickCoords] = useState(null);
  const [shotStats, setShotStats] = useState({
    locationX: 0.0,
    locationY: 0.0,
    shotDistance: 0.0,
    shotZone: "Above the Break 3",
  });

  const [situational, setSituational] = useState({
    period: 1,
    minutesRemaining: 5,
    secondsRemaining: 0,
    shotClock: 12.0,
    defenderDistance: 4.5,
    dribbles: 0,
    touchTime: 1.5,
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCourtClick = (e) => {
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();

    // Convert screen coordinates to SVG viewBox space (0-500, 0-470)
    const scaleX = 500 / rect.width;
    const scaleY = 470 / rect.height;

    const svgX = (e.clientX - rect.left) * scaleX;
    const svgY = (e.clientY - rect.top) * scaleY;

    const details = calculateShotDetails(svgX, svgY);

    setClickCoords({ x: svgX, y: svgY });
    setShotStats(details);
    setPrediction(null); // Reset prediction on click
  };

  const updateSituational = (key, val) => {
    setSituational((prev) => ({ ...prev, [key]: parseFloat(val) || 0 }));
  };

  const handlePredictShot = () => {
    if (!clickCoords) {
      setError("Please click on the court canvas first to register shot coordinates.");
      return;
    }

    setLoading(true);
    setError("");

    const requestData = {
      playerName: selectedPlayer,
      shotDistance: shotStats.shotDistance,
      shotZone: shotStats.shotZone,
      period: situational.period,
      minutesRemaining: situational.minutesRemaining,
      secondsRemaining: situational.secondsRemaining,
      shotClock: situational.shotClock,
      defenderDistance: situational.defenderDistance,
      dribbles: situational.dribbles,
      touchTime: situational.touchTime,
      locationX: shotStats.locationX,
      locationY: shotStats.locationY,
    };

    api.post("/predict-shot", requestData)
      .then((res) => {
        setPrediction(res.data);
      })
      .catch((err) => {
        console.error(err);
        setError("Shot outcome prediction failed. Ensure FastAPI backend is online.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // Trajectory curve
  const getTrajectoryPath = () => {
    if (!clickCoords) return "";
    const startX = clickCoords.x;
    const startY = clickCoords.y;
    const endX = 250;
    const endY = 90; // Hoop center

    const ctrlX = (startX + endX) / 2;
    const ctrlY = Math.min(startY, endY) - 50;

    return `M ${startX},${startY} Q ${ctrlX},${ctrlY} ${endX},${endY}`;
  };

  const renderSlider = (label, key, min, max, step, suffix = "") => {
    return (
      <div style={styles.sliderGroup} key={key}>
        <div style={styles.sliderHeader}>
          <span style={styles.sliderLabel}>{label}</span>
          <span style={styles.sliderValue} className="text-mono">
            {situational[key].toFixed(step >= 1 ? 0 : 1)} {suffix}
          </span>
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={situational[key]}
          onChange={(e) => updateSituational(key, e.target.value)}
        />
      </div>
    );
  };

  const isMade = prediction && prediction.prediction === "Made";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={styles.container}
    >
      {/* Stadium Scoreboard HUD Panel */}
      <div style={styles.scoreboardHUD}>
        <div style={styles.hudBlock}>
          <div style={styles.hudLabel}>PERIOD</div>
          <div style={styles.hudValue} className="text-mono">0{situational.period}</div>
        </div>
        <div style={styles.hudDivider}></div>
        <div style={styles.hudBlock}>
          <div style={styles.hudLabel}>TIME REM.</div>
          <div style={styles.hudValue} className="text-mono">
            {situational.minutesRemaining < 10 ? `0${situational.minutesRemaining}` : situational.minutesRemaining}:
            {situational.secondsRemaining < 10 ? `0${situational.secondsRemaining}` : situational.secondsRemaining}
          </div>
        </div>
        <div style={styles.hudDivider}></div>
        <div style={styles.hudBlock}>
          <div style={styles.hudLabel}>SHOT CLOCK</div>
          <div style={{ ...styles.hudValue, color: situational.shotClock <= 4 ? "var(--color-miss)" : "var(--court-gold)" }} className="text-mono">
            {situational.shotClock.toFixed(1)}s
          </div>
        </div>
        <div style={styles.hudDivider}></div>
        <div style={styles.hudBlock}>
          <div style={styles.hudLabel}>DEFENDER DIST.</div>
          <div style={styles.hudValue} className="text-mono">{situational.defenderDistance.toFixed(1)}ft</div>
        </div>
        <div style={styles.hudDivider}></div>
        <div style={styles.hudBlock}>
          <div style={styles.hudLabel}>DRIBBLES</div>
          <div style={styles.hudValue} className="text-mono">{situational.dribbles}</div>
        </div>
        <div style={styles.hudDivider}></div>
        <div style={styles.hudBlock}>
          <div style={styles.hudLabel}>TOUCH TIME</div>
          <div style={styles.hudValue} className="text-mono">{situational.touchTime.toFixed(1)}s</div>
        </div>
      </div>

      {/* Main content grid */}
      <div style={styles.grid}>
        {/* Left: Court Panel */}
        <div className="sports-card" style={styles.courtCard}>
          <div style={styles.cardHeader}>
            <h3 style={styles.sectionTitle}>Interactive Spatial Map</h3>
            <span style={styles.hudBadge}>CLICK CANVAS TO SELECT SHOT SPOT</span>
          </div>

          <div style={styles.playerContext}>
            <label style={styles.inputLabel}>Shot being predicted for</label>
            <select
              className="form-input"
              value={selectedPlayer}
              onChange={(e) => setSelectedPlayer(e.target.value)}
              style={styles.playerSelect}
            >
              {PLAYER_OPTIONS.map((player) => (
                <option key={player} value={player}>
                  {player}
                </option>
              ))}
            </select>
          </div>

          <svg className="court-svg" viewBox="0 0 500 470" onClick={handleCourtClick}>
            {/* Paint Lane */}
            <rect x="170" y="50" width="160" height="190" className="court-paint" />
            
            {/* Free throw lane circles */}
            <path d="M 190,240 a 60,60 0 0,0 120,0" fill="none" stroke="var(--court-lines)" strokeWidth="2" />
            <path d="M 190,240 a 60,60 0 0,1 120,0" fill="none" stroke="var(--court-lines)" strokeWidth="2" strokeDasharray="6 4" />
            
            {/* Restricted Area */}
            <path d="M 210,90 a 40,40 0 0,0 80,0" fill="none" stroke="var(--court-lines)" strokeWidth="2" />
            
            {/* Backboard and Net Rim */}
            <line x1="220" y1="80" x2="280" y2="80" stroke="var(--court-lines)" strokeWidth="3" />
            <line x1="250" y1="80" x2="250" y2="83" stroke="var(--court-lines)" strokeWidth="3" />
            <circle cx="250" cy="90" r="7.5" fill="none" stroke="var(--court-gold)" strokeWidth="2" />
            
            {/* Three Point Line */}
            <path d="M 30,50 L 30,180 A 237.5,237.5 0 0,0 470,180 L 470,50" className="court-outline" />
            
            {/* Baseline */}
            <line x1="0" y1="50" x2="500" y2="50" stroke="var(--court-lines)" strokeWidth="3" />
            
            {/* Half court boundary */}
            <path d="M 190,470 a 60,60 0 0,1 120,0" fill="none" stroke="var(--court-lines)" strokeWidth="2" />

            {/* Click highlights and path animation */}
            {clickCoords && (
              <g>
                {/* Dotted shot trajectory line */}
                {prediction && (
                  <path
                    d={getTrajectoryPath()}
                    className={`shot-trajectory ${isMade ? "made" : "miss"}`}
                  />
                )}
                
                {/* SVG Native ripple/pulse outer ring indicator */}
                <circle
                  cx={clickCoords.x}
                  cy={clickCoords.y}
                  r="6"
                  fill="none"
                  stroke={prediction ? (isMade ? "var(--color-made)" : "var(--color-miss)") : "var(--court-gold)"}
                  strokeWidth="2"
                  opacity="0.8"
                >
                  <animate attributeName="r" from="6" to="24" dur="1.5s" repeatCount="indefinite" />
                  <animate attributeName="opacity" from="0.9" to="0" dur="1.5s" repeatCount="indefinite" />
                  <animate attributeName="stroke-width" from="3" to="0.5" dur="1.5s" repeatCount="indefinite" />
                </circle>

                {/* Solid center dot representing exact coordinates */}
                <circle
                  cx={clickCoords.x}
                  cy={clickCoords.y}
                  r="6"
                  fill={prediction ? (isMade ? "var(--color-made)" : "var(--color-miss)") : "var(--court-gold)"}
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              </g>
            )}
          </svg>
        </div>

        {/* Right: Scoreboard & Situational Sliders panel */}
        <div style={styles.rightColumn}>
          {/* Outcome report box */}
          <div className="sports-card" style={styles.resultPanel}>
            <div style={styles.cardHeader}>
              <h3 style={styles.sectionTitle}>Outcome Probability HUD</h3>
            </div>

            <div style={styles.playerBadge} className="text-mono">
              {selectedPlayer}
            </div>
            
            {prediction ? (
              <div style={styles.resultBox} className={`sports-card ${isMade ? "made" : "miss"}`}>
                <div style={styles.valueRow}>
                  <div style={styles.valueLabel}>SUCCESS PROBABILITY</div>
                  <div style={{ ...styles.largeValue, color: isMade ? "var(--color-made)" : "var(--color-miss)" }} className="text-mono">
                    {prediction.probability_percent}%
                  </div>
                </div>
                <div style={styles.hudDividerHoriz}></div>
                <div style={styles.outcomeRow}>
                  <span style={styles.outcomeLabel}>REGRESSION DECISION:</span>
                  <span style={{ ...styles.outcomeStatus, color: isMade ? "var(--color-made)" : "var(--color-miss)" }}>
                    {prediction.prediction.toUpperCase()}
                  </span>
                </div>
                {prediction.fallback && (
                  <div className="fallback-badge" style={styles.fallbackBadge}>
                    HEURISTIC STAT FALLBACK
                  </div>
                )}
              </div>
            ) : (
              <div style={styles.hudEmptyState}>
                <div style={styles.emptyIcon}>🏀</div>
                <div style={styles.emptyText}>
                  Click the court to register coordinates, adjust sliders, and run the shot predictor.
                </div>
              </div>
            )}
          </div>

          {/* Sliders configure card */}
          <div className="sports-card" style={styles.slidersCard}>
            <div style={styles.cardHeader}>
              <h3 style={styles.sectionTitle}>Game Situation HUD Log</h3>
            </div>
            
            <div style={styles.coordsDisplay} className="text-mono">
              <div style={styles.coordCol}>
                <div style={styles.coordLabel}>OFFSET LOC X</div>
                <div style={styles.coordVal}>{shotStats.locationX} ft</div>
              </div>
              <div style={styles.coordCol}>
                <div style={styles.coordLabel}>OFFSET LOC Y</div>
                <div style={styles.coordVal}>{shotStats.locationY} ft</div>
              </div>
              <div style={styles.coordCol}>
                <div style={styles.coordLabel}>TOTAL RANGE</div>
                <div style={{ ...styles.coordVal, color: "var(--court-gold)" }}>{shotStats.shotDistance} ft</div>
              </div>
            </div>

            <fieldset style={styles.fieldset}>
              <legend style={styles.legend}>SITUATIONAL CONTEXT</legend>
              {renderSlider("Defender Separation", "defenderDistance", 0.5, 15.0, 0.5, "ft")}
              {renderSlider("Shot Clock Remaining", "shotClock", 0.5, 24.0, 0.5, "s")}
              {renderSlider("Dribbles Prior", "dribbles", 0, 15, 1)}
              {renderSlider("Touch Duration", "touchTime", 0.0, 10.0, 0.5, "s")}
            </fieldset>

            <div style={styles.timeGroup}>
              <div style={{ flex: 1 }}>
                <label style={styles.inputLabel}>Period</label>
                <select 
                  className="form-input" 
                  value={situational.period} 
                  onChange={(e) => updateSituational("period", e.target.value)}
                  style={styles.select}
                >
                  <option value="1">Quarter 1</option>
                  <option value="2">Quarter 2</option>
                  <option value="3">Quarter 3</option>
                  <option value="4">Quarter 4</option>
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={styles.inputLabel}>Clock remaining</label>
                <div style={styles.clockInputs}>
                  <input 
                    type="number" 
                    min="0" 
                    max="12" 
                    className="form-input" 
                    style={styles.clockNumInput}
                    value={situational.minutesRemaining} 
                    onChange={(e) => updateSituational("minutesRemaining", e.target.value)} 
                  />
                  <span style={styles.colon}>:</span>
                  <input 
                    type="number" 
                    min="0" 
                    max="59" 
                    className="form-input" 
                    style={styles.clockNumInput}
                    value={situational.secondsRemaining} 
                    onChange={(e) => updateSituational("secondsRemaining", e.target.value)} 
                  />
                </div>
              </div>
            </div>

            <button 
              className="btn-sports" 
              onClick={handlePredictShot} 
              disabled={loading || !clickCoords}
              style={styles.predictBtn}
            >
              {loading ? <span className="spinner"></span> : "QUERY SHOT PREDICTOR"}
            </button>

            {error && <div className="error-box" style={{ marginTop: 12 }}>{error}</div>}
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
  scoreboardHUD: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-around",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    padding: "12px 16px",
    marginBottom: "24px",
    flexWrap: "wrap",
    gap: "12px",
  },
  hudBlock: {
    textAlign: "center",
    minWidth: "75px",
  },
  hudLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.72rem",
    letterSpacing: "0.05em",
    color: "var(--text-muted)",
    marginBottom: "2px",
  },
  hudValue: {
    fontSize: "1.3rem",
    fontWeight: "bold",
    color: "#fff",
  },
  hudDivider: {
    width: "1px",
    height: "28px",
    background: "var(--border-color)",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1.1fr 1fr",
    gap: "24px",
    alignItems: "start",
  },
  courtCard: {
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    boxSizing: "border-box",
  },
  playerContext: {
    width: "100%",
    marginBottom: "16px",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    width: "100%",
    marginBottom: "16px",
    borderBottom: "1px solid var(--border-color)",
    paddingBottom: "10px",
  },
  sectionTitle: {
    fontFamily: "var(--heading)",
    fontSize: "1.1rem",
    color: "#fff",
  },
  hudBadge: {
    fontFamily: "var(--heading)",
    fontSize: "0.75rem",
    color: "var(--court-gold)",
    letterSpacing: "0.05em",
  },
  rightColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "24px",
  },
  resultPanel: {
    padding: "20px",
    boxSizing: "border-box",
  },
  resultBox: {
    padding: "16px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    textAlign: "left",
  },
  valueRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  valueLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.85rem",
    letterSpacing: "0.05em",
    color: "var(--text-muted)",
  },
  largeValue: {
    fontSize: "2.8rem",
    fontWeight: 700,
  },
  hudDividerHoriz: {
    height: "1px",
    background: "var(--border-color)",
    margin: "12px 0",
  },
  outcomeRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  outcomeLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.85rem",
    letterSpacing: "0.05em",
    color: "var(--text-muted)",
  },
  outcomeStatus: {
    fontFamily: "var(--heading)",
    fontSize: "1.2rem",
    fontWeight: "bold",
    letterSpacing: "0.02em",
  },
  fallbackBadge: {
    background: "rgba(239, 68, 68, 0.1)",
    border: "1px solid rgba(239, 68, 68, 0.2)",
    color: "var(--color-miss)",
    fontSize: "0.68rem",
    fontFamily: "var(--mono)",
    padding: "2px 6px",
    marginTop: "8px",
    borderRadius: "2px",
  },
  hudEmptyState: {
    height: "110px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "14px",
    color: "var(--text-dark)",
    padding: "10px",
  },
  emptyIcon: {
    fontSize: "2rem",
    opacity: 0.15,
  },
  emptyText: {
    fontSize: "0.8rem",
    maxWidth: "240px",
    lineHeight: 1.4,
  },
  slidersCard: {
    padding: "20px",
    boxSizing: "border-box",
  },
  coordsDisplay: {
    display: "flex",
    justifyContent: "space-around",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    padding: "10px",
    borderRadius: "4px",
    marginBottom: "16px",
  },
  coordCol: {
    textAlign: "center",
  },
  coordLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.68rem",
    letterSpacing: "0.05em",
    color: "var(--text-dark)",
    marginBottom: "2px",
  },
  coordVal: {
    fontSize: "0.85rem",
    fontWeight: 600,
    color: "var(--text-main)",
  },
  fieldset: {
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    padding: "14px",
    marginBottom: "16px",
    boxSizing: "border-box",
  },
  legend: {
    fontFamily: "var(--heading)",
    fontSize: "0.75rem",
    fontWeight: 600,
    letterSpacing: "0.05em",
    color: "var(--court-gold)",
    padding: "0 8px",
  },
  sliderGroup: {
    marginBottom: "14px",
    display: "flex",
    flexDirection: "column",
  },
  sliderHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "4px",
  },
  sliderLabel: {
    fontSize: "0.78rem",
    fontWeight: 500,
    color: "var(--text-muted)",
  },
  sliderValue: {
    fontSize: "0.78rem",
    color: "var(--text-main)",
    fontWeight: 600,
  },
  timeGroup: {
    display: "flex",
    gap: "12px",
    marginBottom: "16px",
  },
  inputLabel: {
    display: "block",
    fontFamily: "var(--sans)",
    fontSize: "0.75rem",
    color: "var(--text-muted)",
    marginBottom: "4px",
  },
  playerSelect: {
    width: "100%",
    padding: "8px 12px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    color: "#fff",
  },
  playerBadge: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "4px 10px",
    marginBottom: "12px",
    borderRadius: "999px",
    border: "1px solid rgba(245, 158, 11, 0.25)",
    background: "rgba(245, 158, 11, 0.08)",
    color: "var(--court-gold)",
    fontSize: "0.78rem",
    letterSpacing: "0.03em",
  },
  select: {
    width: "100%",
    padding: "8px 12px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    color: "#fff",
  },
  clockInputs: {
    display: "flex",
    alignItems: "center",
    gap: "4px",
  },
  clockNumInput: {
    width: "100%",
    padding: "8px",
    textAlign: "center",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    color: "#fff",
  },
  predictBtn: {
    width: "100%",
  }
};

export default ShotPredictor;
