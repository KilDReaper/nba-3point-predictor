from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import pandas as pd

curry = players.find_players_by_full_name("Stephen Curry")[0]

shots = shotchartdetail.ShotChartDetail(
    team_id=0,
    player_id=curry["id"],
    season_nullable="2023-24",
    season_type_all_star="Regular Season"
)

df = shots.get_data_frames()[0]

print(df.head())

df.to_csv("curry_2024_shots.csv", index=False)