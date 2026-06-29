import pandas as pd
import numpy as np
from pathlib import Path

INPUT_PATH = Path("ml/data/raw/player_season_stats.csv")
OUTPUT_PATH = Path("ml/data/processed/features.csv")

def engineer_features(df):
    # Sort so lag features are computed in order
    df = df.sort_values(["PLAYER_ID", "SEASON"]).reset_index(drop=True)

    # -- Lag features (previous season stats) --
    grp = df.groupby("PLAYER_ID")
    df["fg3_pct_lag1"] = grp["FG3_PCT"].shift(1)   # last season 3PT%
    df["fg3a_lag1"]    = grp["FG3A"].shift(1)       # last season attempts/game
    df["fg3_pct_lag2"] = grp["FG3_PCT"].shift(2)    # 2 seasons ago
    df["gp_lag1"]      = grp["GP"].shift(1)         # games played last season

    # -- Trend: improvement over last 2 seasons --
    df["fg3_pct_trend"] = df["fg3_pct_lag1"] - df["fg3_pct_lag2"]

    # -- Career average 3PT% up to (but not including) current season --
    df["fg3_pct_career_avg"] = (
        grp["FG3_PCT"]
        .apply(lambda x: x.shift(1).expanding().mean())
        .reset_index(level=0, drop=True)
    )

    # -- Age proxy: seasons in league --
    df["seasons_in_league"] = grp.cumcount()  # 0 = rookie season

    # -- Volume consistency --
    df["fg3a_per_game"] = df["FG3A"]
    df["high_volume"]   = (df["FG3A"] >= 5).astype(int)  # 5+ attempts = volume shooter

    # -- Current season is the TARGET --
    df = df.rename(columns={"FG3_PCT": "target_fg3_pct"})

    # -- Drop rows where we have no lag data (first season for each player) --
    df = df.dropna(subset=["fg3_pct_lag1", "fg3_pct_career_avg"])

    return df

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)
    print(f"Raw data: {len(df)} rows")

    df = engineer_features(df)
    print(f"After feature engineering: {len(df)} rows")

    # Final feature set
    feature_cols = [
        "PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "SEASON",
        "target_fg3_pct",
        "fg3_pct_lag1", "fg3_pct_lag2", "fg3_pct_trend", "fg3_pct_career_avg",
        "fg3a_lag1", "fg3a_per_game", "high_volume",
        "GP", "MIN", "USG_PCT", "AST", "TOV",
        "FG_PCT", "FT_PCT",
        "gp_lag1", "seasons_in_league",
    ]
    available = [c for c in feature_cols if c in df.columns]
    df = df[available]

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved: {OUTPUT_PATH}")
    print(f"\nFeature columns: {[c for c in available if c not in ['PLAYER_ID','PLAYER_NAME','TEAM_ABBREVIATION','SEASON','target_fg3_pct']]}")
    print(f"\nSample:")
    print(df[["PLAYER_NAME", "SEASON", "fg3_pct_lag1", "target_fg3_pct", "fg3_pct_trend"]].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
