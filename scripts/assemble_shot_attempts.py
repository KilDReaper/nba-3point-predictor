from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, playbyplayv3
from pathlib import Path
import pandas as pd
import time

OUT = Path('ml/data/raw')
OUT.mkdir(parents=True, exist_ok=True)

def get_player_id(name: str) -> int:
    matches = players.find_players_by_full_name(name)
    if not matches:
        raise ValueError(f"Player not found: {name}")
    return matches[0]['id']

def get_games_for_player(player_id: int, season: str) -> list[str]:
    gl = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Regular Season')
    df = gl.get_data_frames()[0]
    # Game_ID column may be 'Game_ID' or 'GAME_ID'
    gid_col = None
    for c in df.columns:
        if 'GAME' in c.upper() and 'ID' in c.upper():
            gid_col = c
            break
    if gid_col is None:
        return []
    return df[gid_col].astype(str).tolist()

def extract_shots_from_pbp(game_id: str, player_id: int) -> pd.DataFrame:
    pb = playbyplayv3.PlayByPlayV3(game_id=game_id)
    df = pb.get_data_frames()[0]
    # columns: EVENTNUM, EVENTMSGTYPE, HOMEDESCRIPTION, VISITORDESCRIPTION, PLAYER1_ID, PLAYER1_NAME, etc.
    rows = []
    for _, r in df.iterrows():
        # check player involvement
        if r.get('PLAYER1_ID') == player_id or r.get('PLAYER2_ID') == player_id or r.get('PLAYER3_ID') == player_id:
            desc = (r.get('HOMEDESCRIPTION') or '') + ' ' + (r.get('VISITORDESCRIPTION') or '') + ' ' + (r.get('NEUTRALDESCRIPTION') or '')
            desc = desc.strip()
            if not desc:
                continue
            # detect shot attempts by keywords
            if 'SHOT' in desc.upper() or ' 3PT' in desc.upper() or 'LAYUP' in desc.upper() or 'DUNK' in desc.upper():
                made = 1 if ('MADE' in desc.upper() or 'TIP-IN' in desc.upper() or 'GOOD' in desc.upper()) and 'MISS' not in desc.upper() else 0
                rows.append({'game_id': game_id, 'player_id': player_id, 'description': desc, 'made': made})
    return pd.DataFrame(rows)

def build_dataset(players_list: list[str], seasons: list[str]) -> pd.DataFrame:
    all_rows = []
    for name in players_list:
        pid = get_player_id(name)
        for season in seasons:
            print(f'Gathering games for {name} {season}')
            games = get_games_for_player(pid, season)
            for gid in games:
                try:
                    df = extract_shots_from_pbp(gid, pid)
                    if not df.empty:
                        df['player_name'] = name
                        df['season'] = season
                        all_rows.append(df)
                    time.sleep(0.6)
                except Exception as e:
                    print('pbp error', gid, e)
                    time.sleep(1)
    if all_rows:
        return pd.concat(all_rows, ignore_index=True)
    return pd.DataFrame()

def main():
    players_list = ['Stephen Curry', 'Klay Thompson', 'Damian Lillard']
    seasons = ['2022-23', '2023-24']
    ds = build_dataset(players_list, seasons)
    out = OUT / 'shot_attempts_pbp_2022_2024.csv'
    ds.to_csv(out, index=False)
    print('Saved', out, 'rows', len(ds))

if __name__ == '__main__':
    main()
