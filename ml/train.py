import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

INPUT_PATH = Path("ml/data/processed/features.csv")
MODEL_DIR  = Path("ml/models")

FEATURES = [
    "fg3_pct_lag1", "fg3_pct_lag2", "fg3_pct_trend", "fg3_pct_career_avg",
    "fg3a_lag1", "fg3a_per_game", "high_volume",
    "GP", "MIN", "USG_PCT", "AST", "TOV",
    "FG_PCT", "FT_PCT",
    "gp_lag1", "seasons_in_league",
    "team_encoded",
]
TARGET = "target_fg3_pct"

def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)
    print(f"Dataset: {len(df)} rows\n")

    # Encode team
    le = LabelEncoder()
    df["team_encoded"] = le.fit_transform(df["TEAM_ABBREVIATION"].fillna("UNK"))

    # Drop rows with any NaN in features
    available_features = [f for f in FEATURES if f in df.columns]
    df = df.dropna(subset=available_features + [TARGET])
    print(f"After dropping NaNs: {len(df)} rows")

    X = df[available_features]
    y = df[TARGET]

    
    test_seasons = ["2022-23", "2023-24"]
    test_mask = df["SEASON"].isin(test_seasons)
    X_train, X_test = X[~test_mask], X[test_mask]
    y_train, y_test = y[~test_mask], y[test_mask]
    print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows")

    # Train XGBoost
    model = xgb.XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    mae   = mean_absolute_error(y_test, preds)
    r2    = r2_score(y_test, preds)

    print(f"\nModel Performance:")
    print(f"  MAE:  {mae:.4f}  ({mae*100:.2f} percentage points)")
    print(f"  R^2:  {r2:.4f}")

    # Feature importance
    importance = pd.Series(model.feature_importances_, index=available_features)
    print(f"\nTop features:")
    print(importance.sort_values(ascending=False).head(8).to_string())

    # Sample predictions
    sample = df[test_mask].copy()
    sample["predicted"] = preds
    print(f"\nSample predictions vs actual:")
    print(sample[["PLAYER_NAME", "SEASON", "target_fg3_pct", "predicted"]]
          .head(10)
          .assign(error=lambda x: (x["predicted"] - x["target_fg3_pct"]).abs())
          .to_string(index=False))

    # Save model + encoder
    with open(MODEL_DIR / "forecaster_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(MODEL_DIR / "team_encoder.pkl", "wb") as f:
        pickle.dump(le, f)
    with open(MODEL_DIR / "feature_list.pkl", "wb") as f:
        pickle.dump(available_features, f)

    print(f"\nModel saved to {MODEL_DIR}/")

if __name__ == "__main__":
    main()
