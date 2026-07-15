from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from scripts.preprocessing import FeatureEngineerTransformer


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "processed" / "synthesized_balanced_shots.csv"
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "best_model.pkl"
DEFAULT_REPORT_PATH = ROOT_DIR / "outputs" / "reports" / "shot_model_report.txt"
DEFAULT_METRICS_PATH = ROOT_DIR / "outputs" / "metrics" / "shot_model_metrics.csv"

NUMERIC_FEATURES = ["shotDistance", "period", "minutesRemaining", "secondsRemaining", "locationX", "locationY"]
ENGINEERED_FEATURES = ["gameTimeRemaining", "courtDistance", "lateGameShot", "cornerThree"]
CATEGORICAL_FEATURES = ["shotZone", "playerName"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retrain the NBA shot-level classifier.")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_PATH), help="Path to the shot dataset CSV.")
    parser.add_argument("--model-output", type=str, default=str(DEFAULT_MODEL_PATH), help="Where to save the trained model.")
    parser.add_argument("--report-output", type=str, default=str(DEFAULT_REPORT_PATH), help="Where to save the training report.")
    parser.add_argument("--metrics-output", type=str, default=str(DEFAULT_METRICS_PATH), help="Where to save the metrics CSV.")
    return parser.parse_args()


def make_categorical_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def build_pipeline() -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", make_categorical_encoder()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES + ENGINEERED_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    model = XGBClassifier(
        n_estimators=400,
        learning_rate=0.04,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )

    return Pipeline(
        steps=[
            ("feature_engineer", FeatureEngineerTransformer()),
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def write_report(report_path: Path, lines: list[str]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    model_output = Path(args.model_output)
    report_output = Path(args.report_output)
    metrics_output = Path(args.metrics_output)

    df = pd.read_csv(data_path)
    if "shotMade" not in df.columns:
        raise ValueError(f"Dataset is missing shotMade: {data_path}")

    working = df.copy()
    working["shotMade"] = pd.to_numeric(working["shotMade"], errors="coerce")
    working = working[working["shotMade"].isin([0, 1])].copy()
    working["shotMade"] = working["shotMade"].astype(int)

    feature_frame = working[
        [
            "shotDistance",
            "shotZone",
            "playerName",
            "period",
            "minutesRemaining",
            "secondsRemaining",
            "locationX",
            "locationY",
            "shotMade",
        ]
    ].copy()
    feature_frame = feature_frame.dropna(
        subset=[
            "shotDistance",
            "shotZone",
            "playerName",
            "period",
            "minutesRemaining",
            "secondsRemaining",
            "locationX",
            "locationY",
            "shotMade",
        ]
    )

    X = feature_frame.drop(columns=["shotMade"])
    y = feature_frame["shotMade"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "positive_rate": float(y.mean()),
        "test_rows": int(len(X_test)),
        "train_rows": int(len(X_train)),
    }

    model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_output)

    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(metrics_output, index=False)

    conf = confusion_matrix(y_test, predictions)
    report_lines = [
        "NBA shot-level model retrain report",
        "",
        f"Data path: {data_path}",
        f"Rows used: {len(feature_frame)}",
        f"Train rows: {len(X_train)}",
        f"Test rows: {len(X_test)}",
        f"Positive rate: {metrics['positive_rate']:.4f}",
        f"Accuracy: {metrics['accuracy']:.4f}",
        f"F1: {metrics['f1']:.4f}",
        f"ROC-AUC: {metrics['roc_auc']:.4f}",
        "",
        "Confusion matrix:",
        str(conf),
        "",
        "Classification report:",
        classification_report(y_test, predictions, zero_division=0),
    ]
    write_report(report_output, report_lines)

    print(f"Saved model to {model_output}")
    print(f"Saved metrics to {metrics_output}")
    print(f"Saved report to {report_output}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1: {metrics['f1']:.4f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")


if __name__ == "__main__":
    main()