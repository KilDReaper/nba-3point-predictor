from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts.config import (
    ENGINEERED_COLUMNS,
    LATE_GAME_SECONDS_THRESHOLD,
    NUMERIC_COLUMNS,
    OUTLIER_COLUMNS,
    PROCESSED_DIR,
    RAW_DIR,
    RAW_NUMERIC_COLUMNS,
    REPORTS_DIR,
    REQUIRED_COLUMNS,
    TARGET_COLUMN,
)
from scripts.utils import ensure_project_directories, write_text_file


def load_dataset(dataset_path: str | Path | None = None) -> pd.DataFrame:
    if dataset_path is None:
        csv_files = sorted(RAW_DIR.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")
        dataset_file = csv_files[0]
    else:
        dataset_file = Path(dataset_path)
        if dataset_file.is_dir():
            csv_files = sorted(dataset_file.glob("*.csv"))
            if not csv_files:
                raise FileNotFoundError(f"No CSV files found in {dataset_file}")
            dataset_file = csv_files[0]

    if not dataset_file.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_file}")
    return pd.read_csv(dataset_file)


def harmonize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map common NBA shot-chart column names to the pipeline's expected schema.

    This function detects uppercase NBA/Gamelog style headers and renames them to
    the expected pipeline names. Missing expected columns are left as NaN so
    downstream imputation can handle them.
    """

    # Candidate sources (priority order for fields with multiple possible names)
    candidates = {
        "playerName": ["PLAYER_NAME", "PLAYER"],
        "team": ["TEAM_NAME", "TEAM"],
        "season": ["SEASON"],
        "gameDate": ["GAME_DATE"],
        "shotDistance": ["SHOT_DISTANCE", "SHOT_DIST"],
        "shotZone": ["SHOT_ZONE_BASIC", "SHOT_ZONE_AREA", "SHOT_ZONE_RANGE"],
        "period": ["PERIOD"],
        "minutesRemaining": ["MINUTES_REMAINING"],
        "secondsRemaining": ["SECONDS_REMAINING"],
        "shotClock": ["SHOT_CLOCK"],
        "defenderDistance": ["DEFENDER_DISTANCE"],
        "dribbles": ["DRIBBLES"],
        "touchTime": ["TOUCH_TIME"],
        "locationX": ["LOC_X", "XLOC"],
        "locationY": ["LOC_Y", "YLOC"],
        "shotMade": ["SHOT_MADE_FLAG"],
        "shotAttempted": ["SHOT_ATTEMPTED_FLAG"],
        "eventType": ["EVENT_TYPE"],
    }

    df = df.copy()
    rename_map: dict[str, str] = {}
    for dst, src_list in candidates.items():
        # only map if destination not already present to avoid duplicate column names
        if dst in df.columns:
            continue
        for src in src_list:
            if src in df.columns:
                rename_map[src] = dst
                break

    if rename_map:
        df = df.rename(columns=rename_map)

    # If season is missing but GAME_DATE exists, derive season year
    if "season" not in df.columns and "gameDate" in df.columns:
        try:
            df["season"] = pd.to_datetime(df["gameDate"], errors="coerce").dt.year
        except Exception:
            df["season"] = "unknown"

    # Ensure all required pipeline columns exist (create with NaN if missing)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    return df


def validate_dataset(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    for column in RAW_NUMERIC_COLUMNS:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    return working


def _remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working = working[working[TARGET_COLUMN].isin([0, 1])]
    working = working[working["shotDistance"].between(0, 100, inclusive="both") | working["shotDistance"].isna()]
    working = working[working["period"].between(1, 20, inclusive="both") | working["period"].isna()]
    working = working[working["minutesRemaining"].between(0, 12, inclusive="both") | working["minutesRemaining"].isna()]
    working = working[working["secondsRemaining"].between(0, 59, inclusive="both") | working["secondsRemaining"].isna()]
    working = working[working["shotClock"].between(0, 24, inclusive="both") | working["shotClock"].isna()]
    working = working[working["defenderDistance"].between(0, 30, inclusive="both") | working["defenderDistance"].isna()]
    working = working[working["dribbles"].between(0, 30, inclusive="both") | working["dribbles"].isna()]
    working = working[working["touchTime"].between(0, 30, inclusive="both") | working["touchTime"].isna()]
    working = working[working["locationX"].between(-30, 30, inclusive="both") | working["locationX"].isna()]
    working = working[working["locationY"].between(-10, 50, inclusive="both") | working["locationY"].isna()]
    return working


def _remove_outliers_iqr(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    working = df.copy()
    for column in columns:
        series = working[column].dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        working = working[working[column].between(lower_bound, upper_bound, inclusive="both") | working[column].isna()]
    return working


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working["gameTimeRemaining"] = (
        ((working["period"].fillna(1) - 1) * 12 * 60)
        + (working["minutesRemaining"].fillna(0) * 60)
        + working["secondsRemaining"].fillna(0)
    ).clip(lower=0)
    working["courtDistance"] = np.sqrt(working["locationX"].fillna(0) ** 2 + working["locationY"].fillna(0) ** 2)
    working["lateGameShot"] = (working["gameTimeRemaining"] <= LATE_GAME_SECONDS_THRESHOLD).astype(int)
    working["cornerThree"] = (
        (working["shotDistance"].fillna(0) >= 22.0)
        & (working["locationX"].fillna(0).abs() >= 22.0)
        & (working["locationY"].fillna(0).abs() <= 7.8)
    ).astype(int)
    return working


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    # Attempt to harmonize common NBA shot-chart column names first
    df = harmonize_columns(df)
    validate_dataset(df)

    working = df.copy()
    rows_before = len(working)
    missing_before = working.isna().sum().to_dict()

    working = working.drop_duplicates()
    duplicates_removed = rows_before - len(working)

    working = _coerce_numeric(working)
    working = _remove_invalid_rows(working)
    working = _remove_outliers_iqr(working, OUTLIER_COLUMNS)

    for column in ["playerName", "team", "season", "shotZone"]:
        working[column] = working[column].astype("string").fillna("Unknown").replace({"": "Unknown"})

    medians = working[NUMERIC_COLUMNS].median(numeric_only=True)
    for column in NUMERIC_COLUMNS:
        working[column] = working[column].fillna(medians[column])

    target_mode = working[TARGET_COLUMN].mode(dropna=True)
    target_fill = int(target_mode.iloc[0]) if not target_mode.empty else 0
    working[TARGET_COLUMN] = working[TARGET_COLUMN].fillna(target_fill).astype(int)
    working = engineer_features(working)
    working = working.reset_index(drop=True)

    report = {
        "rows_before": int(rows_before),
        "rows_after": int(len(working)),
        "duplicates_removed": int(duplicates_removed),
        "missing_before": {key: int(value) for key, value in missing_before.items()},
        "missing_after": {key: int(value) for key, value in working.isna().sum().to_dict().items()},
        "class_distribution": {str(key): int(value) for key, value in working[TARGET_COLUMN].value_counts().to_dict().items()},
        "engineered_columns": ENGINEERED_COLUMNS,
    }
    return working, report


def save_clean_dataset(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    ensure_project_directories()
    output_file = Path(output_path) if output_path is not None else (PROCESSED_DIR / "cleaned_nba_shots.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    return output_file


def save_quality_report(report: dict[str, Any], output_path: str | Path | None = None) -> Path:
    ensure_project_directories()
    output_file = Path(output_path) if output_path is not None else (REPORTS_DIR / "data_quality_report.txt")
    lines: list[str] = ["NBA 3-Point Shot Data Quality Report", ""]
    lines.append(f"Rows before cleaning: {report['rows_before']}")
    lines.append(f"Rows after cleaning: {report['rows_after']}")
    lines.append(f"Duplicates removed: {report['duplicates_removed']}")
    lines.append("")
    lines.append("Class distribution:")
    for key, value in report["class_distribution"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Missing values before cleaning:")
    for key, value in sorted(report["missing_before"].items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Missing values after cleaning:")
    for key, value in sorted(report["missing_after"].items()):
        lines.append(f"- {key}: {value}")
    write_text_file(output_file, lines)
    return output_file
