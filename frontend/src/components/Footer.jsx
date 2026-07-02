import { FaGithub, FaBasketballBall } from "react-icons/fa";

function Footer() {
  return (
    <footer style={styles.footer}>
      <div style={styles.container}>
        <div style={styles.left}>
          <FaBasketballBall style={styles.icon} />
          <span style={styles.text}>
            © {new Date().getFullYear()} NBA 3PT Cast • Final Year Project
          </span>
        </div>
        <div style={styles.right}>
          <a 
            href="https://github.com/KilDReaper/nba-3point-predictor" 
            target="_blank" 
            rel="noopener noreferrer" 
            style={styles.link}
          >
            <FaGithub style={styles.githubIcon} /> GitHub Repo
          </a>
        </div>
      </div>
    </footer>
  );
}

const styles = {
  footer: {
    background: "rgba(11, 14, 20, 0.5)",
    borderTop: "1px solid var(--glass-border)",
    padding: "20px 40px",
    marginTop: "auto",
    width: "100%",
    boxSizing: "border-box",
  },
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "16px",
  },
  left: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  icon: {
    color: "var(--court-gold)",
    fontSize: "1.1rem",
  },
  text: {
    color: "var(--text-muted)",
    fontSize: "0.8rem",
    fontWeight: 500,
  },
  right: {
    display: "flex",
    alignItems: "center",
  },
  link: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    color: "var(--text-muted)",
    textDecoration: "none",
    fontSize: "0.8rem",
    fontWeight: 600,
    transition: "color 0.2s ease",
  },
  githubIcon: {
    fontSize: "1rem",
  }
};

export default Footer;
