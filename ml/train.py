import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import Ridge
import xgboost as xgb

INPUT_PATH = Path("ml/data/processed/features.csv")
MODEL_DIR  = Path("ml/models")
PLOTS_DIR  = Path("ml/outputs/plots")
METRICS_DIR  = Path("ml/outputs/metrics")

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
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)
    print(f"Dataset Loaded: {len(df)} rows\n")

    # Encode team
    le = LabelEncoder()
    df["team_encoded"] = le.fit_transform(df["TEAM_ABBREVIATION"].fillna("UNK"))

    # Drop rows with any NaN in features or target
    available_features = [f for f in FEATURES if f in df.columns]
    df = df.dropna(subset=available_features + [TARGET])
    print(f"After dropping NaNs: {len(df)} rows")

    X = df[available_features]
    y = df[TARGET]

    # Split: Train on older seasons, Test on 2022-23 and 2023-24
    test_seasons = ["2022-23", "2023-24"]
    test_mask = df["SEASON"].isin(test_seasons)
    X_train, X_test = X[~test_mask], X[test_mask]
    y_train, y_test = y[~test_mask], y[test_mask]
    
    print(f"Train size: {len(X_train)} rows | Test size: {len(X_test)} rows\n")

    # Scale features (necessary for Ridge Regression baseline)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Train XGBoost Regressor
    xgb_params = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 4,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
    }
    xgb_model = xgb.XGBRegressor(**xgb_params)
    xgb_model.fit(X_train, y_train) # XGBoost handles unscaled data well

    # 2. Train Ridge Regression Baseline
    ridge_params = {
        "alpha": 1.0,
        "random_state": 42
    }
    ridge_model = Ridge(**ridge_params)
    ridge_model.fit(X_train_scaled, y_train)

    # Predictions
    xgb_preds = xgb_model.predict(X_test)
    ridge_preds = ridge_model.predict(X_test_scaled)

    # Evaluate XGBoost
    xgb_mae = mean_absolute_error(y_test, xgb_preds)
    xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
    xgb_r2 = r2_score(y_test, xgb_preds)

    # Evaluate Ridge
    ridge_mae = mean_absolute_error(y_test, ridge_preds)
    ridge_rmse = np.sqrt(mean_squared_error(y_test, ridge_preds))
    ridge_r2 = r2_score(y_test, ridge_preds)

    print("Model Evaluation Metrics on Test Set (2022-23 & 2023-24):")
    print(f"{'Metric':<10} | {'XGBoost Regressor':<18} | {'Ridge Baseline (Scaled)':<22}")
    print("-" * 60)
    print(f"{'MAE':<10} | {xgb_mae:.6f} ({xgb_mae*100:.2f}%)  | {ridge_mae:.6f} ({ridge_mae*100:.2f}%)")
    print(f"{'RMSE':<10} | {xgb_rmse:.6f} ({xgb_rmse*100:.2f}%)  | {ridge_rmse:.6f} ({ridge_rmse*100:.2f}%)")
    print(f"{'R²':<10} | {xgb_r2:.6f}            | {ridge_r2:.6f}")
    print("-" * 60 + "\n")

    # Save metrics to CSV
    metrics_df = pd.DataFrame({
        "Model": ["XGBoost", "Ridge Baseline"],
        "MAE": [xgb_mae, ridge_mae],
        "RMSE": [xgb_rmse, ridge_rmse],
        "R2": [xgb_r2, ridge_r2],
        "Train_Size": [len(X_train), len(X_train)],
        "Test_Size": [len(X_test), len(X_test)]
    })
    metrics_df.to_csv(METRICS_DIR / "season_model_metrics.csv", index=False)

    # Save example predictions table
    sample_results = df[test_mask].copy()
    sample_results["XGB_Predicted"] = xgb_preds
    sample_results["Ridge_Predicted"] = ridge_preds
    sample_results["XGB_Error"] = (sample_results["XGB_Predicted"] - sample_results[TARGET]).abs()
    sample_results["Ridge_Error"] = (sample_results["Ridge_Predicted"] - sample_results[TARGET]).abs()

    print("Sample Predictions (First 10 Players):")
    cols_to_print = ["PLAYER_NAME", "SEASON", TARGET, "XGB_Predicted", "Ridge_Predicted", "XGB_Error", "Ridge_Error"]
    print(sample_results[cols_to_print].head(10).to_string(index=False))

    # Save outputs
    with open(MODEL_DIR / "forecaster_model.pkl", "wb") as f:
        pickle.dump(xgb_model, f)
    with open(MODEL_DIR / "ridge_baseline_model.pkl", "wb") as f:
        pickle.dump(ridge_model, f)
    with open(MODEL_DIR / "team_encoder.pkl", "wb") as f:
        pickle.dump(le, f)
    with open(MODEL_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(MODEL_DIR / "feature_list.pkl", "wb") as f:
        pickle.dump(available_features, f)
    print(f"\nSaved models and encoders to {MODEL_DIR}")

    # Generate and save actual vs predicted scatter plot
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        plt.scatter(y_test * 100, xgb_preds * 100, alpha=0.6, label=f"XGBoost (MAE: {xgb_mae*100:.2f}%)", color="#ff7f0e", edgecolors='w', s=50)
        plt.scatter(y_test * 100, ridge_preds * 100, alpha=0.5, label=f"Ridge Baseline (MAE: {ridge_mae*100:.2f}%)", color="#1f77b4", marker="s", edgecolors='w', s=40)
        
        # Ideal prediction line
        min_val = min(y_test.min(), xgb_preds.min(), ridge_preds.min()) * 100
        max_val = max(y_test.max(), xgb_preds.max(), ridge_preds.max()) * 100
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label="Perfect Forecast (y = x)")
        
        plt.title("NBA 3-Point % Forecast Comparison: XGBoost vs Ridge Baseline", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Actual 3-Point Percentage (FG3%)", fontsize=12)
        plt.ylabel("Predicted 3-Point Percentage (FG3%)", fontsize=12)
        plt.xlim(min_val - 2, max_val + 2)
        plt.ylim(min_val - 2, max_val + 2)
        plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none")
        plt.tight_layout()
        
        plot_path = PLOTS_DIR / "season_comparison.png"
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print(f"Comparison plot saved to {plot_path}")
    except ImportError:
        print("Warning: matplotlib or seaborn not installed. Skipping plot generation.")

if __name__ == "__main__":
    main()
