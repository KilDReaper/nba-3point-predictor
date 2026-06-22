from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT_DIR / "models"
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"
OUTPUTS_DIR = ROOT_DIR / "outputs"
METRICS_DIR = OUTPUTS_DIR / "metrics"
PLOTS_DIR = OUTPUTS_DIR / "plots"
REPORTS_DIR = OUTPUTS_DIR / "reports"

TARGET_COLUMN = "shotMade"
REQUIRED_COLUMNS = [
    "playerName",
    "team",
    "season",
    "shotDistance",
    "shotZone",
    "period",
    "minutesRemaining",
    "secondsRemaining",
    "shotClock",
    "defenderDistance",
    "dribbles",
    "touchTime",
    "locationX",
    "locationY",
    TARGET_COLUMN,
]

NUMERIC_COLUMNS = [
    "shotDistance",
    "period",
    "minutesRemaining",
    "secondsRemaining",
    "shotClock",
    "defenderDistance",
    "dribbles",
    "touchTime",
    "locationX",
    "locationY",
]

ENGINEERED_COLUMNS = ["gameTimeRemaining", "courtDistance", "lateGameShot", "cornerThree"]
LABEL_ENCODE_COLUMNS = ["playerName", "team", "season"]
ONE_HOT_COLUMNS = ["shotZone"]
MODEL_FEATURE_COLUMNS = NUMERIC_COLUMNS + ENGINEERED_COLUMNS + ONE_HOT_COLUMNS
PREDICTION_INPUT_COLUMNS = [
    "shotDistance",
    "shotZone",
    "period",
    "minutesRemaining",
    "secondsRemaining",
    "shotClock",
    "defenderDistance",
    "dribbles",
    "touchTime",
    "locationX",
    "locationY",
]

RAW_NUMERIC_COLUMNS = NUMERIC_COLUMNS + [TARGET_COLUMN]
BASE_NUMERIC_COLUMNS = NUMERIC_COLUMNS
BASE_NUMERIC_FEATURES = NUMERIC_COLUMNS
PROCESSED_DATA_DIR = PROCESSED_DIR
RAW_DATA_DIR = RAW_DIR

RANDOM_STATE = 42
TEST_SIZE = 0.2
SHOT_CLOCK_MAX = 24.0
MINUTES_PER_PERIOD = 12.0
SECONDS_PER_MINUTE = 60.0
CORNER_THREE_X_THRESHOLD = 22.0
CORNER_THREE_Y_THRESHOLD = 7.8
LATE_GAME_SECONDS_THRESHOLD = 120.0
OUTLIER_COLUMNS = [
    "shotDistance",
    "shotClock",
    "defenderDistance",
    "dribbles",
    "touchTime",
    "locationX",
    "locationY",
]

QUALITY_OUTLIER_COLUMNS = OUTLIER_COLUMNS
