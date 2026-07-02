import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { FaSearch, FaSlidersH, FaBasketballBall } from "react-icons/fa";
import api from "../services/api";
import Hero from "../components/Hero";
import ModelInfo from "../components/ModelInfo";

function Home() {
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    api.get("/model-info")
      .then((res) => setModelInfo(res.data))
      .catch((err) => console.error("Error loading model info:", err));
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      style={styles.container}
    >
      {/* Hero scoreboard statistics HUD */}
      <Hero modelInfo={modelInfo} />

      {/* Primary Billboard Banner (Scoreboard look) */}
      <div className="sports-card primary" style={styles.introCard}>
        <h1 style={styles.title}>NBA Three-Point Analytics Forecaster</h1>
        <p style={styles.subtitle}>
          An analytics platform using Gradient Boosted Trees (XGBoost) to regress seasonal player metrics and forecast spatial individual shot probabilities.
        </p>
        <div style={styles.btnRow}>
          <Link to="/player" className="btn-sports" style={styles.heroLink}>
            <FaSearch /> Player History
          </Link>
          <Link 
            to="/court" 
            className="btn-sports" 
            style={{ 
              ...styles.heroLink, 
              background: "#2f80ed", 
              border: "1px solid #1d6ed1", 
              color: "#fff" 
            }}
          >
            <FaBasketballBall /> Shot Predictor
          </Link>
        </div>
      </div>

      {/* Grid of features */}
      <div style={styles.grid}>
        <div className="sports-card" style={styles.featureCard}>
          <div style={{ ...styles.iconBg, color: "var(--court-gold)" }}>
            <FaSearch size={20} />
          </div>
          <h3 style={styles.featTitle}>Player Profile Lookup</h3>
          <p style={styles.featText}>
            Review shooting metrics of active NBA players. Compare actual season results against model predictions.
          </p>
        </div>

        <div className="sports-card" style={styles.featureCard}>
          <div style={{ ...styles.iconBg, color: "var(--accent-blue)" }}>
            <FaSlidersH size={20} />
          </div>
          <h3 style={styles.featTitle}>Custom Season Forecast</h3>
          <p style={styles.featText}>
            Adjust usage rates, playtime logs, and shooting accuracies in our form to regress theoretical outcomes.
          </p>
        </div>

        <div className="sports-card" style={styles.featureCard}>
          <div style={{ ...styles.iconBg, color: "var(--color-made)" }}>
            <FaBasketballBall size={20} />
          </div>
          <h3 style={styles.featTitle}>Spatial Shot Simulator</h3>
          <p style={styles.featText}>
            Click coordinates on our vector basketball court to calculate shot clock and defender separation probabilities.
          </p>
        </div>
      </div>

      {/* Model Info block */}
      <ModelInfo modelInfo={modelInfo} />
    </motion.div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
  },
  introCard: {
    width: "100%",
    padding: "40px 24px",
    textAlign: "center",
    marginBottom: "24px",
    boxSizing: "border-box",
    background: "radial-gradient(circle at center, #1b212f 0%, #121620 100%)",
  },
  title: {
    fontFamily: "var(--heading)",
    fontSize: "2.4rem",
    fontWeight: 700,
    color: "#fff",
    marginBottom: "12px",
    letterSpacing: "0.01em",
  },
  subtitle: {
    fontSize: "0.95rem",
    color: "var(--text-muted)",
    maxWidth: "700px",
    margin: "0 auto 24px",
    lineHeight: 1.5,
  },
  btnRow: {
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    flexWrap: "wrap",
  },
  heroLink: {
    textDecoration: "none",
    width: "auto",
    padding: "10px 24px",
    fontSize: "0.9rem",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "24px",
    width: "100%",
    marginBottom: "24px",
  },
  featureCard: {
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    textAlign: "center",
    boxSizing: "border-box",
  },
  iconBg: {
    width: "48px",
    height: "48px",
    borderRadius: "4px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "16px",
  },
  featTitle: {
    fontFamily: "var(--heading)",
    fontSize: "1.1rem",
    fontWeight: 600,
    marginBottom: "8px",
    color: "var(--text-main)",
  },
  featText: {
    fontSize: "0.85rem",
    color: "var(--text-muted)",
    lineHeight: 1.5,
  }
};

export default Home;
