import React, { useState, useEffect, useRef } from "react";
import api from "../services/api";
import { FaSearch } from "react-icons/fa";

const SHORTCUTS = ["Stephen Curry", "Klay Thompson", "Damian Lillard", "James Harden"];

function PlayerSearch({ onSelectPlayer }) {
  const [query, setQuery] = useState("");
  const [allPlayers, setAllPlayers] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Load player list from backend
    api.get("/players")
      .then((res) => {
        if (res.data && res.data.players) {
          setAllPlayers(res.data.players);
        }
      })
      .catch((err) => {
        console.error("Failed to load player list:", err);
      });

    // Close dropdown on outside click
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleInputChange = (val) => {
    setQuery(val);
    if (val.length < 2) {
      setFiltered([]);
      setShowDropdown(false);
      return;
    }
    const matches = allPlayers
      .filter((p) => p.toLowerCase().includes(val.toLowerCase()))
      .slice(0, 8);
    setFiltered(matches);
    setShowDropdown(matches.length > 0);
  };

  const handleSelect = (name) => {
    setQuery(name);
    setShowDropdown(false);
    onSelectPlayer(name);
  };

  const handleSearchClick = () => {
    if (query.trim()) {
      onSelectPlayer(query.trim());
      setShowDropdown(false);
    }
  };

  return (
    <div style={styles.searchWrapper} ref={dropdownRef}>
      <div style={styles.inputWrapper}>
        <input
          type="text"
          className="form-input"
          style={styles.searchInput}
          placeholder="Search player name..."
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => {
            if (filtered.length > 0) setShowDropdown(true);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearchClick();
          }}
        />
        <button style={styles.searchBtn} onClick={handleSearchClick}>
          <FaSearch />
        </button>
      </div>
      
      {showDropdown && (
        <div className="search-dropdown" style={styles.dropdown}>
          {filtered.map((p) => (
            <div
              key={p}
              className="search-item"
              style={styles.dropdownItem}
              onClick={() => handleSelect(p)}
            >
              {p}
            </div>
          ))}
        </div>
      )}

      {/* Quick search tags suggestions */}
      <div style={styles.shortcutsRow}>
        <span style={styles.shortcutLabel}>PROFILES:</span>
        {SHORTCUTS.map((name) => (
          <button 
            key={name} 
            style={styles.shortcutBtn}
            onClick={() => handleSelect(name)}
          >
            {name.split(" ")[1] /* display only last name */}
          </button>
        ))}
      </div>
    </div>
  );
}

const styles = {
  searchWrapper: {
    position: "relative",
    width: "100%",
  },
  inputWrapper: {
    display: "flex",
    alignItems: "center",
    position: "relative",
  },
  searchInput: {
    width: "100%",
    padding: "10px 40px 10px 14px",
    background: "#08090c",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    color: "var(--text-main)",
    fontSize: "0.9rem",
    outline: "none",
  },
  searchBtn: {
    position: "absolute",
    right: "12px",
    background: "none",
    border: "none",
    color: "var(--court-gold)",
    cursor: "pointer",
    fontSize: "0.95rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  dropdown: {
    position: "absolute",
    top: "calc(100% + 4px)",
    left: 0,
    right: 0,
    background: "var(--panel-bg)",
    border: "1px solid var(--border-color)",
    borderRadius: "4px",
    maxHeight: "220px",
    overflowY: "auto",
    zIndex: 1000,
    boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
  },
  dropdownItem: {
    padding: "10px 14px",
    cursor: "pointer",
    fontSize: "0.85rem",
    borderBottom: "1px solid rgba(255, 255, 255, 0.03)",
  },
  shortcutsRow: {
    display: "flex",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "6px",
    marginTop: "10px",
  },
  shortcutLabel: {
    fontFamily: "var(--heading)",
    fontSize: "0.72rem",
    fontWeight: 600,
    letterSpacing: "0.05em",
    color: "var(--text-dark)",
    marginRight: "4px",
  },
  shortcutBtn: {
    background: "#1f2633",
    border: "none",
    color: "var(--text-muted)",
    padding: "3px 8px",
    borderRadius: "3px",
    fontSize: "0.75rem",
    fontWeight: 500,
    cursor: "pointer",
    transition: "all 0.1s ease",
  }
};

export default PlayerSearch;
