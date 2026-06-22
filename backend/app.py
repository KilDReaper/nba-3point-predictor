from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from io import StringIO

# Add ml module to path
ml_path = Path(__file__).resolve().parents[1] / "ml"
sys.path.insert(0, str(ml_path))

from scripts.pipeline_utils import load_best_model
from scripts.preprocessing import prepare_prediction_frame
from scripts.config import MODELS_DIR

app = FastAPI(title="NBA 3-Point Shot Predictor API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance (loaded once at startup)
model = None

@app.on_event("startup")
async def load_model():
    global model
    try:
        model = load_best_model()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise


class ShotPredictionRequest(BaseModel):
    """Single shot prediction request"""
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


class ShotPredictionResponse(BaseModel):
    """Single shot prediction response"""
    prediction: str
    probability: float
    input_params: dict


class BatchPredictionResponse(BaseModel):
    """Batch predictions response"""
    total: int
    successful: int
    failed: int
    predictions: list


class ModelInfoResponse(BaseModel):
    """Model information and metrics"""
    model_type: str
    accuracy: float
    f1_score: float
    roc_auc: float
    training_rows: int
    positive_rate: float


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "NBA 3-Point Shot Predictor", "version": "1.0.0"}


@app.post("/predict", response_model=ShotPredictionResponse, tags=["Prediction"])
async def predict_shot(request: ShotPredictionRequest):
    """Predict whether a single 3-point shot will be made"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        frame = prepare_prediction_frame(
            shotDistance=request.shotDistance,
            shotZone=request.shotZone,
            period=request.period,
            minutesRemaining=request.minutesRemaining,
            secondsRemaining=request.secondsRemaining,
            shotClock=request.shotClock,
            defenderDistance=request.defenderDistance,
            dribbles=request.dribbles,
            touchTime=request.touchTime,
            locationX=request.locationX,
            locationY=request.locationY,
        )
        
        probability = float(model.predict_proba(frame)[0, 1])
        prediction = "Made" if probability >= 0.5 else "Missed"
        
        return ShotPredictionResponse(
            prediction=prediction,
            probability=round(probability, 4),
            input_params=request.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict-batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(file: UploadFile = File(...)):
    """Batch predict from CSV upload (columns: shotDistance, shotZone, period, minutesRemaining, secondsRemaining, shotClock, defenderDistance, dribbles, touchTime, locationX, locationY)"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode()))
        
        required_cols = [
            "shotDistance", "shotZone", "period", "minutesRemaining", "secondsRemaining",
            "shotClock", "defenderDistance", "dribbles", "touchTime", "locationX", "locationY"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        predictions = []
        successful = 0
        for idx, row in df.iterrows():
            try:
                frame = prepare_prediction_frame(
                    shotDistance=float(row["shotDistance"]),
                    shotZone=str(row["shotZone"]),
                    period=int(row["period"]),
                    minutesRemaining=float(row["minutesRemaining"]),
                    secondsRemaining=float(row["secondsRemaining"]),
                    shotClock=float(row["shotClock"]),
                    defenderDistance=float(row["defenderDistance"]),
                    dribbles=float(row["dribbles"]),
                    touchTime=float(row["touchTime"]),
                    locationX=float(row["locationX"]),
                    locationY=float(row["locationY"]),
                )
                prob = float(model.predict_proba(frame)[0, 1])
                pred = "Made" if prob >= 0.5 else "Missed"
                predictions.append({"row": idx, "prediction": pred, "probability": round(prob, 4)})
                successful += 1
            except Exception as e:
                predictions.append({"row": idx, "error": str(e)})
        
        return BatchPredictionResponse(
            total=len(df),
            successful=successful,
            failed=len(df) - successful,
            predictions=predictions
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Info"])
async def get_model_info():
    """Get model metadata and performance metrics"""
    try:
        return ModelInfoResponse(
            model_type="XGBoost",
            accuracy=0.9890,
            f1_score=0.9904,
            roc_auc=0.9930,
            training_rows=904,
            positive_rate=0.5664
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
