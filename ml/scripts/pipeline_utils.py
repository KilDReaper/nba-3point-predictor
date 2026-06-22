from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from scripts.config import MODELS_DIR


def save_training_artifacts(
    best_model: Any,
    encoders: Any,
    scaler: Any,
    model_path: str | Path = MODELS_DIR / "best_model.pkl",
    encoders_path: str | Path = MODELS_DIR / "encoders.pkl",
    scaler_path: str | Path = MODELS_DIR / "scaler.pkl",
) -> None:
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, Path(model_path))
    joblib.dump(encoders, Path(encoders_path))
    joblib.dump(scaler, Path(scaler_path))


def load_best_model(model_path: str | Path = MODELS_DIR / "best_model.pkl") -> Any:
    return joblib.load(Path(model_path))