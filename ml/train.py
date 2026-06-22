from __future__ import annotations

import argparse

import pandas as pd
from sklearn.metrics import roc_curve

from scripts.config import METRICS_DIR, PLOTS_DIR, PROCESSED_DIR, REPORTS_DIR, TARGET_COLUMN
from scripts.data_processing import clean_dataset, load_dataset, save_clean_dataset, save_quality_report
from scripts.models import build_model_pipelines, evaluate_classifier, extract_feature_importance
from scripts.pipeline_utils import save_training_artifacts
from scripts.preprocessing import build_train_test_split, fit_auxiliary_encoders, split_features_target
from scripts.reporting import create_model_report
from scripts.utils import ensure_project_directories, setup_logging
from scripts.visualization import save_confusion_matrix, save_correlation_heatmap, save_feature_importance_plot, save_roc_curve


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Train the NBA 3-point shot prediction models.")
	parser.add_argument("--data", type=str, default=None, help="Path to a CSV file or directory containing the raw dataset.")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	logger = setup_logging("nba_3point_train")
	ensure_project_directories()

	logger.info("Loading dataset")
	raw_df = load_dataset(args.data)
	cleaned_df, quality_report = clean_dataset(raw_df)

	cleaned_path = save_clean_dataset(cleaned_df, PROCESSED_DIR / "cleaned_nba_shots.csv")
	report_path = save_quality_report(quality_report, REPORTS_DIR / "data_quality_report.txt")

	encoders = fit_auxiliary_encoders(cleaned_df)
	save_training_artifacts(None, encoders, encoders.scaler)

	features, target = split_features_target(cleaned_df)
	X_train, X_test, y_train, y_test = build_train_test_split(features, target)

	model_pipelines = build_model_pipelines()
	comparison_rows: list[dict[str, float | str]] = []
	fitted_models: dict[str, object] = {}

	for model_name, pipeline in model_pipelines.items():
		logger.info("Training %s", model_name)
		pipeline.fit(X_train, y_train)
		metrics = evaluate_classifier(pipeline, X_test, y_test)
		comparison_rows.append(
			{
				"model": model_name,
				"accuracy": metrics["accuracy"],
				"precision": metrics["precision"],
				"recall": metrics["recall"],
				"f1": metrics["f1"],
				"roc_auc": metrics["roc_auc"],
			}
		)
		fitted_models[model_name] = pipeline

	comparison_df = pd.DataFrame(comparison_rows).sort_values("f1", ascending=False).reset_index(drop=True)
	best_model_name = str(comparison_df.iloc[0]["model"])
	best_model = fitted_models[best_model_name]
	best_metrics = evaluate_classifier(best_model, X_test, y_test)
	feature_importance = extract_feature_importance(best_model)

	save_training_artifacts(best_model, encoders, encoders.scaler)
	METRICS_DIR.mkdir(parents=True, exist_ok=True)
	comparison_df.to_csv(METRICS_DIR / "model_comparison.csv", index=False)
	pd.DataFrame([
		{
			"model": best_model_name,
			"accuracy": best_metrics["accuracy"],
			"precision": best_metrics["precision"],
			"recall": best_metrics["recall"],
			"f1": best_metrics["f1"],
			"roc_auc": best_metrics["roc_auc"],
		}
	]).to_csv(METRICS_DIR / "best_model_metrics.csv", index=False)

	confusion_matrix_path = save_confusion_matrix(best_metrics["confusion_matrix"], PLOTS_DIR / "confusion_matrix.png")
	fpr, tpr, _ = roc_curve(y_test, best_metrics["probabilities"])
	roc_curve_path = save_roc_curve(fpr, tpr, best_metrics["roc_auc"], PLOTS_DIR / "roc_curve.png")
	importance_path = save_feature_importance_plot(feature_importance, PLOTS_DIR / "feature_importance.png")
	correlation_path = save_correlation_heatmap(cleaned_df, PLOTS_DIR / "correlation_heatmap.png")

	feature_columns = [
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
		"gameTimeRemaining",
		"courtDistance",
		"lateGameShot",
		"cornerThree",
	]
	feature_statistics = cleaned_df[feature_columns].describe().reset_index().rename(columns={"index": "statistic"})
	dataset_summary = {
		"rows": len(cleaned_df),
		"columns": len(cleaned_df.columns),
		"positive_rate": float(cleaned_df[TARGET_COLUMN].mean()),
		"cleaned_dataset_path": str(cleaned_path),
		"quality_report_path": str(report_path),
		"plot_paths": [str(confusion_matrix_path), str(roc_curve_path), str(importance_path), str(correlation_path)],
	}

	report_file = create_model_report(
		dataset_summary=dataset_summary,
		feature_statistics=feature_statistics,
		model_comparison=comparison_df,
		best_model_name=best_model_name,
		feature_importance=feature_importance,
		output_path=REPORTS_DIR / "model_report.txt",
	)
	logger.info("Saved model report to %s", report_file)
	logger.info("Best model selected: %s", best_model_name)


if __name__ == "__main__":
	main()
