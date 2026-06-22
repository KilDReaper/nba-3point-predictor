from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from scripts.config import BASE_NUMERIC_FEATURES, ENGINEERED_COLUMNS, ONE_HOT_COLUMNS, RANDOM_STATE
from scripts.preprocessing import FeatureEngineerTransformer


def build_preprocessor() -> ColumnTransformer:
    numeric_features = BASE_NUMERIC_FEATURES + ENGINEERED_COLUMNS
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    try:
        categorical_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        categorical_encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", categorical_encoder),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, ONE_HOT_COLUMNS),
        ],
        remainder="drop",
    )


def build_model_pipelines() -> dict[str, Pipeline]:
    estimators: dict[str, Any] = {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=1.0,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            tree_method="hist",
        ),
    }

    return {
        name: Pipeline(
            steps=[
                ("feature_engineer", FeatureEngineerTransformer()),
                ("preprocessor", build_preprocessor()),
                ("model", estimator),
            ]
        )
        for name, estimator in estimators.items()
    }


def evaluate_classifier(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "probabilities": probabilities,
        "predictions": predictions,
    }


def extract_feature_importance(model: Pipeline) -> pd.DataFrame:
    preprocessor = model.named_steps["preprocessor"]
    model_estimator = model.named_steps["model"]

    feature_names = list(BASE_NUMERIC_FEATURES + ENGINEERED_COLUMNS)
    categorical_encoder = preprocessor.named_transformers_["categorical"].named_steps["encoder"]
    feature_names.extend(categorical_encoder.get_feature_names_out(ONE_HOT_COLUMNS).tolist())

    if hasattr(model_estimator, "feature_importances_"):
        importances = np.asarray(model_estimator.feature_importances_)
    elif hasattr(model_estimator, "coef_"):
        importances = np.abs(np.asarray(model_estimator.coef_)).ravel()
    else:
        importances = np.zeros(len(feature_names), dtype=float)

    # Handle mismatch between computed feature names and model importances
    if len(importances) != len(feature_names):
        # prefer model's feature count when available
        n = len(importances)
        feature_names = [f"feature_{i}" for i in range(n)]

    df = pd.DataFrame({"feature": feature_names, "importance": importances})
    return df.sort_values("importance", ascending=False).reset_index(drop=True)
