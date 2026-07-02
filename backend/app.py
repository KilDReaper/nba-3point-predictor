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
sys.path.insert(0, str(Path("ml").resolve()))

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
    return {
        "model_type": "XGBoost Regressor",
        "mae": 0.0276,
        "r2": 0.3031,
        "training_rows": 1222,
        "test_rows": 488,
        "seasons": "2014-15 to 2023-24",
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
    }

@app.post("/predict")
def predict(req: PredictRequest):
    # Encode team
    team = req.team if req.team in team_encoder.classes_ else "UNK"
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
        "input": req.model_dump(),
    }

class ShotPredictRequest(BaseModel):
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
            
        prob = max(0.10, min(0.75, prob))
        prediction = "Made" if prob >= 0.43 else "Missed"
        
        return {
            "prediction": prediction,
            "probability": round(prob, 3),
            "probability_percent": round(prob * 100, 1),
            "fallback": True,
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
        
        probability = float(shot_model.predict_proba(frame)[0, 1])
        prediction = "Made" if probability >= 0.5 else "Missed"
        
        return {
            "prediction": prediction,
            "probability": round(probability, 3),
            "probability_percent": round(probability * 100, 1),
            "fallback": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shot prediction error: {str(e)}")
