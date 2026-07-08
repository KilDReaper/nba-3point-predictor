import React from "react";

const TEAM_OPTIONS = [
  "ATL", "BKN", "BOS", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
  "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
  "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS",
];

function PredictionForm({ form, onChange, onSubmit, loading }) {
  const updateVal = (key, val) => {
    onChange(key, parseFloat(val) || 0);
  };

  const renderSlider = (label, key, min, max, step, displayMul = 1, isPercent = false) => {
    const valDisp = isPercent
      ? (form[key] * displayMul).toFixed(1) + "%"
      : (form[key] * displayMul).toFixed(step >= 1 ? 0 : 1);

    return (
      <div style={styles.formGroup} key={key}>
        <div style={styles.labelRow}>
          <label style={styles.label}>{label}</label>
          <span className="form-value-badge" style={styles.badge}>
            {valDisp}
          </span>
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={form[key]}
          onChange={(e) => updateVal(key, e.target.value)}
        />
      </div>
    );
  };

  return (
    <div className="sports-card" style={styles.card}>
      <div style={styles.title}>Simulate Player Parameters</div>

      <fieldset style={styles.fieldset}>
        <legend style={styles.legend}>TEAM CONTEXT</legend>
        <div style={styles.formGroup}>
          <div style={styles.labelRow}>
            <label style={styles.label}>Team</label>
            <span className="form-value-badge" style={styles.badge}>
              {form.team}
            </span>
          </div>
          <select
            className="form-input"
            value={form.team}
            onChange={(e) => onChange("team", e.target.value)}
            style={styles.select}
          >
            {TEAM_OPTIONS.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>
        </div>
      </fieldset>
      
      <fieldset style={styles.fieldset}>
        <legend style={styles.legend}>SHOOTING PROFILE</legend>
        {renderSlider("3PT% Last Season", "fg3_pct_last_season", 0.20, 0.50, 0.005, 100, true)}
        {renderSlider("Overall Field Goal %", "fg_pct", 0.30, 0.60, 0.005, 100, true)}
        {renderSlider("Free Throw %", "ft_pct", 0.50, 0.98, 0.005, 100, true)}
        {renderSlider("3PA per Game", "fg3a_per_game", 1.0, 15.0, 0.1)}
      </fieldset>

      <fieldset style={styles.fieldset}>
        <legend style={styles.legend}>VOLUMETRICS & AGE</legend>
        {renderSlider("Usage Rate %", "usg_pct", 10.0, 40.0, 0.5)}
        {renderSlider("Minutes / Game", "minutes_per_game", 5.0, 42.0, 0.5)}
        {renderSlider("Games Played", "games_played", 10, 82, 1)}
        {renderSlider("Seasons in League", "seasons_in_league", 1, 20, 1)}
      </fieldset>
      
      <button 
        className="btn-sports" 
        onClick={onSubmit} 
        disabled={loading} 
        style={styles.submitBtn}
      >
        {loading ? <span className="spinner"></span> : "RUN XGBOOST FORECASTER"}
      </button>
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
  formGroup: {
    marginBottom: "14px",
    display: "flex",
    flexDirection: "column",
  },
  labelRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "4px",
  },
  label: {
    fontSize: "0.78rem",
    fontWeight: 500,
    color: "var(--text-muted)",
  },
  badge: {
    fontFamily: "var(--mono)",
    fontSize: "0.78rem",
    color: "var(--text-main)",
    fontWeight: 600,
  },
  select: {
    width: "100%",
    padding: "8px 12px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    color: "#fff",
  },
  submitBtn: {
    marginTop: "4px",
    width: "100%",
  }
};

export default PredictionForm;
