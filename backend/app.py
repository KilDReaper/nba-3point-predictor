from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

app = FastAPI(title="NBA 3PT% Forecaster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "ml" / "models"
DATA_PATH = BASE_DIR / "ml" / "data" / "processed" / "features.csv"

with open(MODEL_DIR / "forecaster_model.pkl", "rb") as f:
    model = pickle.load(f)
with open(MODEL_DIR / "team_encoder.pkl", "rb") as f:
    team_encoder = pickle.load(f)
with open(MODEL_DIR / "feature_list.pkl", "rb") as f:
    feature_list = pickle.load(f)

# Set up sys.path to resolve 'scripts' module from ml/
import sys
sys.path.insert(0, str((BASE_DIR / "ml").resolve()))

# Load shot-level model safely using joblib
try:
    import joblib
    with open(MODEL_DIR / "best_model.pkl", "rb") as f:
        shot_model = joblib.load(f)
    shot_model_loaded = True
    print("Shot-level ML model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load shot-level model: {e}")
    shot_model = None
    shot_model_loaded = False

df = pd.read_csv(DATA_PATH)
df["team_encoded"] = team_encoder.transform(
    df["TEAM_ABBREVIATION"].fillna("UNK").apply(
        lambda x: x if x in team_encoder.classes_ else "UNK"
    )
)

PLAYER_BASELINES = (
    df.groupby("PLAYER_NAME")[["target_fg3_pct", "fg3_pct_career_avg", "fg3a_per_game"]]
    .mean(numeric_only=True)
    .round(4)
    .to_dict(orient="index")
)
LEAGUE_BASELINE = float(df["target_fg3_pct"].mean())


def get_player_adjustment(player_name: str) -> tuple[float, dict[str, float]]:
    profile = PLAYER_BASELINES.get(player_name)
    if not profile:
        return 0.0, {}

    skill_anchor = float(profile.get("fg3_pct_career_avg", LEAGUE_BASELINE))
    volume_anchor = float(profile.get("fg3a_per_game", 0.0))

    skill_delta = skill_anchor - LEAGUE_BASELINE
    volume_delta = min(max((volume_anchor - 6.0) / 10.0, -0.15), 0.15)
    adjustment = (skill_delta * 0.85) + (volume_delta * 0.25)

    return adjustment, {
        "career_avg": round(skill_anchor, 4),
        "volume_per_game": round(volume_anchor, 2),
        "adjustment": round(adjustment, 4),
    }


def safe_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return numeric


def get_next_season_label(season: object) -> str:
    season_text = str(season)
    try:
        start_year = int(season_text.split("-")[0])
        return f"{start_year + 1}-{str(start_year + 2)[-2:]}"
    except (TypeError, ValueError, IndexError):
        return f"{season_text} (Next)"


def build_next_season_features(player: pd.DataFrame) -> dict[str, float]:
    latest_row = player.iloc[-1]
    previous_row = player.iloc[-2] if len(player) > 1 else latest_row

    last_actual = safe_float(latest_row.get("target_fg3_pct", latest_row.get("fg3_pct_lag1", 0.0)))
    prev_actual = safe_float(previous_row.get("target_fg3_pct", previous_row.get("fg3_pct_lag1", last_actual)))
    career_avg = safe_float(player["target_fg3_pct"].mean(), last_actual)
    attempts_per_game = safe_float(latest_row.get("fg3a_per_game", latest_row.get("fg3a_lag1", 0.0)))
    games_played = safe_float(latest_row.get("GP", latest_row.get("gp_lag1", 0.0)))
    minutes_per_game = safe_float(latest_row.get("MIN", 0.0))
    usage_rate = safe_float(latest_row.get("USG_PCT", 0.0))
    assists = safe_float(latest_row.get("AST", 0.0))
    turnovers = safe_float(latest_row.get("TOV", 0.0))
    field_goal_pct = safe_float(latest_row.get("FG_PCT", 0.0))
    free_throw_pct = safe_float(latest_row.get("FT_PCT", 0.0))
    team_abbreviation = str(latest_row.get("TEAM_ABBREVIATION", "UNK"))
    team = team_abbreviation if team_abbreviation in team_encoder.classes_ else "UNK"

    return {
        "fg3_pct_lag1": last_actual,
        "fg3_pct_lag2": prev_actual,
        "fg3_pct_trend": last_actual - prev_actual,
        "fg3_pct_career_avg": career_avg,
        "fg3a_lag1": attempts_per_game,
        "fg3a_per_game": attempts_per_game,
        "high_volume": int(attempts_per_game >= 5),
        "GP": games_played,
        "MIN": minutes_per_game,
        "USG_PCT": usage_rate,
        "AST": assists,
        "TOV": turnovers,
        "FG_PCT": field_goal_pct,
        "FT_PCT": free_throw_pct,
        "gp_lag1": games_played,
        "seasons_in_league": safe_float(latest_row.get("seasons_in_league", len(player) - 1)) + 1,
        "team": team,
    }


def predict_next_season(player: pd.DataFrame) -> dict[str, object]:
    next_features = build_next_season_features(player)
    team = next_features.pop("team")
    team_enc = int(team_encoder.transform([team])[0])

    row = pd.DataFrame([{feature: next_features.get(feature, 0) for feature in feature_list}])
    row["team_encoded"] = team_enc

    prediction = float(model.predict(row)[0])
    latest_season = player["SEASON"].iloc[-1]

    return {
        "season": get_next_season_label(latest_season),
        "source_season": latest_season,
        "predicted_fg3_pct": round(prediction, 3),
        "predicted_fg3_pct_percent": round(prediction * 100, 1),
    }

# -- Schemas --
class PredictRequest(BaseModel):
    fg3_pct_last_season: float
    fg3a_per_game: float
    games_played: float
    minutes_per_game: float
    fg_pct: float
    ft_pct: float
    usg_pct: float
    ast_per_game: float
    tov_per_game: float
    seasons_in_league: int
    team: str = "UNK"

# -- Routes --
@app.get("/")
def health():
    return {"status": "ok", "model": "NBA 3PT% Forecaster"}

@app.get("/model-info")
def model_info():
    available_features = [feature for feature in feature_list if feature in df.columns]
    cleaned = df.dropna(subset=available_features + ["target_fg3_pct"])
    test_seasons = ["2022-23", "2023-24"]
    test_mask = cleaned["SEASON"].isin(test_seasons)

    return {
        "model_type": "XGBoost Regressor",
        "mae": 0.0276,
        "r2": 0.2763,
        "training_rows": int((~test_mask).sum()),
        "test_rows": int(test_mask.sum()),
        "seasons": f"{df['SEASON'].min()} to {df['SEASON'].max()}",
        "features": feature_list,
    }

@app.get("/players")
def get_players():
    players = (
        df.groupby("PLAYER_ID")["PLAYER_NAME"]
        .first()
        .reset_index()
        .sort_values("PLAYER_NAME")
    )
    return {"players": players["PLAYER_NAME"].tolist(), "count": len(players)}

@app.get("/player/{player_name}")
def get_player(player_name: str):
    matches = df[df["PLAYER_NAME"].str.lower() == player_name.lower()]
    if matches.empty:
        # Try partial match
        matches = df[df["PLAYER_NAME"].str.lower().str.contains(player_name.lower())]
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")

    player = matches.sort_values("SEASON")
    available = [f for f in feature_list if f in player.columns]
    player_features = player[available].fillna(0)
    predictions = model.predict(player_features)

    history = []
    for i, (_, row) in enumerate(player.iterrows()):
        history.append({
            "season": row["SEASON"],
            "actual_fg3_pct": round(float(row["target_fg3_pct"]), 3),
            "predicted_fg3_pct": round(float(predictions[i]), 3),
            "fg3a_per_game": round(float(row["fg3a_per_game"]), 1),
            "games_played": int(row["GP"]),
        })

    return {
        "player": player["PLAYER_NAME"].iloc[0],
        "seasons": len(history),
        "history": history,
        "next_season_prediction": predict_next_season(player),
    }

@app.post("/predict")
def predict(req: PredictRequest):
    # Encode team
    default_team = str(team_encoder.classes_[0])
    team = req.team if req.team in team_encoder.classes_ else default_team
    team_enc = int(team_encoder.transform([team])[0])

    input_data = {
        "fg3_pct_lag1": req.fg3_pct_last_season,
        "fg3_pct_lag2": req.fg3_pct_last_season,
        "fg3_pct_trend": 0.0,
        "fg3_pct_career_avg": req.fg3_pct_last_season,
        "fg3a_lag1": req.fg3a_per_game,
        "fg3a_per_game": req.fg3a_per_game,
        "high_volume": int(req.fg3a_per_game >= 5),
        "GP": req.games_played,
        "MIN": req.minutes_per_game,
        "USG_PCT": req.usg_pct,
        "AST": req.ast_per_game,
        "TOV": req.tov_per_game,
        "FG_PCT": req.fg_pct,
        "FT_PCT": req.ft_pct,
        "gp_lag1": req.games_played,
        "seasons_in_league": req.seasons_in_league,
        "team_encoded": team_enc,
    }

    row = pd.DataFrame([{f: input_data.get(f, 0) for f in feature_list}])
    prediction = float(model.predict(row)[0])

    return {
        "predicted_fg3_pct": round(prediction, 3),
        "predicted_fg3_pct_percent": round(prediction * 100, 1),
        "resolved_team": team,
        "input": req.model_dump(),
    }

class ShotPredictRequest(BaseModel):
    playerName: str = "Stephen Curry"
    shotDistance: float
    shotZone: str
    period: int
    minutesRemaining: float
    secondsRemaining: float
    shotClock: float
    defenderDistance: float
    dribbles: float
    touchTime: float
    locationX: float
    locationY: float

@app.post("/predict-shot")
def predict_shot(req: ShotPredictRequest):
    player_adjustment, player_profile = get_player_adjustment(req.playerName)

    if not shot_model_loaded or shot_model is None:
        # Fallback to intelligent basketball physics heuristic
        prob = 0.36
        
        dist = req.shotDistance
        if dist > 23.75:
            prob -= (dist - 23.75) * 0.02
        elif dist < 22.0:
            prob += 0.05
            
        def_dist = req.defenderDistance
        if def_dist >= 6.0:
            prob += 0.06
        elif def_dist <= 2.0:
            prob -= 0.10
        else:
            prob += (def_dist - 4.0) * 0.02
            
        sc = req.shotClock
        if sc <= 4.0:
            prob -= (4.0 - sc) * 0.03
        elif sc >= 18.0:
            prob += 0.02
            
        drib = req.dribbles
        if drib == 0:
            prob += 0.03
        elif drib > 3:
            prob -= (drib - 3) * 0.015
            
        tt = req.touchTime
        if tt > 6.0:
            prob -= 0.03

        prob += player_adjustment
            
        prob = max(0.10, min(0.75, prob))
        prediction = "Made" if prob >= 0.43 else "Missed"
        
        return {
            "prediction": prediction,
            "probability": round(prob, 3),
            "probability_percent": round(prob * 100, 1),
            "fallback": True,
            "playerName": req.playerName,
            "playerProfile": player_profile,
            "message": "Heuristic fallback prediction (Shot-level ML model not loaded on server)"
        }

    try:
        from scripts.preprocessing import prepare_prediction_frame
        frame = prepare_prediction_frame(
            shotDistance=req.shotDistance,
            shotZone=req.shotZone,
            period=req.period,
            minutesRemaining=req.minutesRemaining,
            secondsRemaining=req.secondsRemaining,
            shotClock=req.shotClock,
            defenderDistance=req.defenderDistance,
            dribbles=req.dribbles,
            touchTime=req.touchTime,
            locationX=req.locationX,
            locationY=req.locationY,
        )
        
        probability = float(shot_model.predict_proba(frame)[0, 1]) + player_adjustment
        probability = float(np.clip(probability, 0.0, 1.0))
        prediction = "Made" if probability >= 0.5 else "Missed"
        
        return {
            "prediction": prediction,
            "probability": round(probability, 3),
            "probability_percent": round(probability * 100, 1),
            "fallback": False,
            "playerName": req.playerName,
            "playerProfile": player_profile,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shot prediction error: {str(e)}")
