from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from scripts.config import (
    BASE_NUMERIC_FEATURES,
    ENGINEERED_COLUMNS,
    LABEL_ENCODE_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    ONE_HOT_COLUMNS,
    PREDICTION_INPUT_COLUMNS,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
)
from scripts.data_processing import engineer_features
from scripts.utils import make_dense_one_hot_encoder


@dataclass(slots=True)
class AuxiliaryEncoders:
    label_encoders: dict[str, LabelEncoder]
    one_hot_encoder: OneHotEncoder
    scaler: StandardScaler


class FeatureEngineerTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y: Any = None) -> "FeatureEngineerTransformer":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return engineer_features(pd.DataFrame(X))


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    features = df[PREDICTION_INPUT_COLUMNS].copy()
    target = df[TARGET_COLUMN].astype(int).copy()
    return features, target


def build_train_test_split(
    features: pd.DataFrame,
    target: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        stratify=target,
        random_state=RANDOM_STATE,
    )


def fit_auxiliary_encoders(df: pd.DataFrame) -> AuxiliaryEncoders:
    label_encoders: dict[str, LabelEncoder] = {}
    for column in LABEL_ENCODE_COLUMNS:
        encoder = LabelEncoder()
        encoder.fit(df[column].astype(str).fillna("Unknown"))
        label_encoders[column] = encoder

    one_hot_encoder = make_dense_one_hot_encoder()
    one_hot_encoder.fit(df[ONE_HOT_COLUMNS].astype(str).fillna("Unknown"))

    scaler = StandardScaler()
    scaler.fit(df[BASE_NUMERIC_FEATURES + ENGINEERED_COLUMNS])

    return AuxiliaryEncoders(
        label_encoders=label_encoders,
        one_hot_encoder=one_hot_encoder,
        scaler=scaler,
    )


def prepare_prediction_frame(
    shotDistance: float,
    shotZone: str,
    period: int,
    minutesRemaining: float,
    secondsRemaining: float,
    shotClock: float,
    defenderDistance: float,
    dribbles: float,
    touchTime: float,
    locationX: float,
    locationY: float,
) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "shotDistance": [shotDistance],
            "shotZone": [shotZone],
            "period": [period],
            "minutesRemaining": [minutesRemaining],
            "secondsRemaining": [secondsRemaining],
            "shotClock": [shotClock],
            "defenderDistance": [defenderDistance],
            "dribbles": [dribbles],
            "touchTime": [touchTime],
            "locationX": [locationX],
            "locationY": [locationY],
        }
    )
    return frame
