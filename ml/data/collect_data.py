import time
import pandas as pd
from pathlib import Path
from nba_api.stats.endpoints import leaguedashplayerstats

SEASONS = [f"{y}-{str(y+1)[-2:]}" for y in range(2014, 2024)]
MIN_3PA = 50
DELAY = 0.7
OUTPUT_PATH = Path("ml/data/raw/player_season_stats.csv")

KEEP_COLS = [
    "PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION",
    "GP", "MIN", "FG3M", "FG3A", "FG3_PCT",
    "FGM", "FGA", "FG_PCT",
    "FTM", "FTA", "FT_PCT",
    "AST", "TOV", "USG_PCT", "SEASON",
]

def fetch_season(season):
    print(f"  Fetching {season}...", end=" ")
    try:
        result = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            per_mode_detailed="PerGame",
            season_type_all_star="Regular Season",
        )
        df = result.get_data_frames()[0]
        df["SEASON"] = season
        df["FG3A_TOTAL"] = df["FG3A"] * df["GP"]
        df = df[df["FG3A_TOTAL"] >= MIN_3PA].copy()
        print(f"{len(df)} players")
        return df
    except Exception as e:
        print(f"ERROR: {e}")
        return pd.DataFrame()

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_seasons = []
    print(f"Collecting {len(SEASONS)} seasons...\n")
    for season in SEASONS:
        df = fetch_season(season)
        if not df.empty:
            available = [c for c in KEEP_COLS if c in df.columns]
            all_seasons.append(df[available])
        time.sleep(DELAY)
    combined = pd.concat(all_seasons, ignore_index=True)
    combined = combined.drop_duplicates(subset=["PLAYER_ID", "SEASON"])
    combined = combined.sort_values(["PLAYER_NAME", "SEASON"]).reset_index(drop=True)
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nDone! Rows: {len(combined)}, Players: {combined['PLAYER_ID'].nunique()}, Seasons: {combined['SEASON'].nunique()}")
    print(combined[["PLAYER_NAME", "SEASON", "FG3A", "FG3_PCT", "GP"]].head(10).to_string(index=False))

if __name__ == "__main__":
    main()