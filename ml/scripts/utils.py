from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import joblib
from sklearn.preprocessing import OneHotEncoder

from scripts.config import (
    METRICS_DIR,
    MODELS_DIR,
    OUTPUTS_DIR,
    PLOTS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
)


def ensure_project_directories() -> None:
    """Create the project output folders if they do not already exist."""

    for directory in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        MODELS_DIR,
        OUTPUTS_DIR,
        METRICS_DIR,
        PLOTS_DIR,
        REPORTS_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def setup_logging(name: str = "nba_3point_pipeline") -> logging.Logger:
    """Configure console and file logging for the pipeline."""

    ensure_project_directories()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    log_file = OUTPUTS_DIR / "pipeline.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def find_first_csv(directory: Path) -> Path:
    """Return the first CSV file in a directory, sorted alphabetically."""

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    csv_files = sorted(directory.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {directory}")
    return csv_files[0]


def resolve_dataset_path(explicit_path: str | Path | None) -> Path:
    """Resolve a dataset path or fall back to the raw data directory."""

    if explicit_path is not None:
        path = Path(explicit_path)
        if path.is_dir():
            return find_first_csv(path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        return path

    return find_first_csv(RAW_DATA_DIR)


def make_dense_one_hot_encoder() -> OneHotEncoder:
    """Create a OneHotEncoder with dense output across scikit-learn versions."""

    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def save_joblib_object(obj: object, path: Path) -> None:
    """Persist a Python object using Joblib."""

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_joblib_object(path: Path) -> object:
    """Load a Joblib artifact from disk."""

    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return joblib.load(path)


def format_percentage(value: float) -> str:
    return f"{value * 100:.2f}%"


def write_text_file(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
