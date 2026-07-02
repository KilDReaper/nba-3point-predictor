import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

function NotFound() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      style={styles.container}
    >
      <div className="glass-card" style={styles.card}>
        <div style={styles.emoji}>🏀</div>
        <h1 style={styles.title}>404 - Airball!</h1>
        <p style={styles.text}>
          The page you are looking for has bounced off the rim and out of bounds.
        </p>
        <Link to="/" className="btn-glow" style={styles.button}>
          Back to Dashboard
        </Link>
      </div>
    </motion.div>
  );
}

const styles = {
  container: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "60vh",
    width: "100%",
  },
  card: {
    padding: "48px 32px",
    textAlign: "center",
    maxWidth: "480px",
    width: "100%",
  },
  emoji: {
    fontSize: "4rem",
    marginBottom: "16px",
    animation: "bounce 2s infinite",
  },
  title: {
    fontFamily: "'Outfit', sans-serif",
    fontSize: "2.2rem",
    fontWeight: 800,
    color: "#fff",
    marginBottom: "12px",
  },
  text: {
    fontSize: "0.95rem",
    color: "var(--text-muted)",
    lineHeight: 1.5,
    marginBottom: "28px",
  },
  button: {
    textDecoration: "none",
    width: "auto",
    padding: "12px 28px",
    display: "inline-flex",
  }
};

export default NotFound;
