from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("ml/data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_player_shots(player_name: str, season: str) -> pd.DataFrame:
    matches = players.find_players_by_full_name(player_name)
    if not matches:
        raise ValueError(f"Player not found: {player_name}")
    pid = matches[0]["id"]
    sc = shotchartdetail.ShotChartDetail(team_id=0, player_id=pid, season_nullable=season, season_type_all_star="Regular Season")
    df = sc.get_data_frames()[0]
    return df

def save_player_season(player_name: str, season: str) -> Path:
    df = fetch_player_shots(player_name, season)
    safe_name = player_name.lower().replace(" ", "_")
    out = OUTPUT_DIR / f"{safe_name}_{season.replace('-', '')}_shots.csv"
    df.to_csv(out, index=False)
    return out

def main():
    players_to_fetch = ["Klay Thompson", "Damian Lillard"]
    seasons = ["2022-23", "2023-24"]
    saved = []
    for p in players_to_fetch:
        for s in seasons:
            print(f"Fetching {p} {s}...")
            try:
                path = save_player_season(p, s)
                print(f"Saved: {path}")
                saved.append(path)
            except Exception as e:
                print(f"Error fetching {p} {s}: {e}")
    # also create a combined CSV
    if saved:
        combined = pd.concat([pd.read_csv(p) for p in saved], ignore_index=True)
        combined_path = OUTPUT_DIR / "players_klay_lillard_2022-2024_shots.csv"
        combined.to_csv(combined_path, index=False)
        print(f"Combined saved: {combined_path}")

if __name__ == '__main__':
    main()
