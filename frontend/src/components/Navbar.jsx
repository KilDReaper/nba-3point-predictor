import { NavLink } from "react-router-dom";
import { FaBasketballBall } from "react-icons/fa";

function Navbar() {
  return (
    <header style={styles.header}>
      <NavLink to="/" style={styles.logoContainer}>
        <FaBasketballBall style={styles.logoIcon} />
        <span style={styles.logoText}>3PT<span style={styles.logoSpan}>Cast</span></span>
      </NavLink>
      
      <nav style={styles.nav}>
        <NavLink 
          to="/" 
          end
          style={({ isActive }) => ({
            ...styles.navLink,
            ...(isActive ? styles.navActive : {})
          })}
        >
          Dashboard
        </NavLink>
        
        <NavLink 
          to="/player" 
          style={({ isActive }) => ({
            ...styles.navLink,
            ...(isActive ? styles.navActive : {})
          })}
        >
          Player Lookup
        </NavLink>
        
        <NavLink 
          to="/predict" 
          style={({ isActive }) => ({
            ...styles.navLink,
            ...(isActive ? styles.navActive : {})
          })}
        >
          Custom Forecast
        </NavLink>
        
        <NavLink 
          to="/court" 
          style={({ isActive }) => ({
            ...styles.navLink,
            ...(isActive ? styles.navActive : {})
          })}
        >
          Shot Predictor
        </NavLink>
      </nav>
    </header>
  );
}

const styles = {
  header: {
    background: "#08090c",
    padding: "0 24px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: "64px",
    borderBottom: "1px solid var(--border-color)",
    position: "sticky",
    top: 0,
    zIndex: 1000,
    boxSizing: "border-box",
  },
  logoContainer: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    textDecoration: "none",
  },
  logoIcon: {
    fontSize: "1.4rem",
    color: "var(--court-gold)",
  },
  logoText: {
    fontFamily: "var(--heading)",
    fontWeight: 700,
    fontSize: "1.4rem",
    textTransform: "uppercase",
    letterSpacing: "0.02em",
    color: "var(--text-main)",
  },
  logoSpan: {
    color: "var(--court-gold)",
    marginLeft: "2px",
  },
  nav: {
    display: "flex",
    gap: "4px",
  },
  navLink: {
    color: "var(--text-muted)",
    fontFamily: "var(--heading)",
    fontSize: "0.9rem",
    fontWeight: 500,
    textTransform: "uppercase",
    letterSpacing: "0.03em",
    padding: "6px 12px",
    cursor: "pointer",
    borderRadius: "3px",
    textDecoration: "none",
    transition: "all 0.15s ease",
  },
  navActive: {
    color: "var(--text-main)",
    borderBottom: "2px solid var(--court-gold)",
    borderRadius: "0px",
  }
};

export default Navbar;
