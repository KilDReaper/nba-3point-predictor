from __future__ import annotations

import argparse

import pandas as pd
from sklearn.metrics import roc_curve

from scripts.config import METRICS_DIR, PLOTS_DIR, PROCESSED_DIR
from scripts.data_processing import load_dataset
from scripts.models import evaluate_classifier
from scripts.pipeline_utils import load_best_model
from scripts.preprocessing import build_train_test_split, split_features_target
from scripts.utils import setup_logging
from scripts.visualization import save_confusion_matrix, save_roc_curve


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Evaluate the saved NBA 3-point shot model.")
	parser.add_argument("--data", type=str, default=str(PROCESSED_DIR / "cleaned_nba_shots.csv"), help="Path to the cleaned dataset.")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	logger = setup_logging("nba_3point_evaluate")

	df = load_dataset(args.data)
	features, target = split_features_target(df)
	_, X_test, _, y_test = build_train_test_split(features, target)

	model = load_best_model()
	metrics = evaluate_classifier(model, X_test, y_test)

	METRICS_DIR.mkdir(parents=True, exist_ok=True)
	pd.DataFrame(
		[
			{
				"accuracy": metrics["accuracy"],
				"precision": metrics["precision"],
				"recall": metrics["recall"],
				"f1": metrics["f1"],
				"roc_auc": metrics["roc_auc"],
			}
		]
	).to_csv(METRICS_DIR / "evaluation_metrics.csv", index=False)

	save_confusion_matrix(metrics["confusion_matrix"], PLOTS_DIR / "confusion_matrix_eval.png")
	fpr, tpr, _ = roc_curve(y_test, metrics["probabilities"])
	save_roc_curve(fpr, tpr, metrics["roc_auc"], PLOTS_DIR / "roc_curve_eval.png")

	logger.info("Evaluation complete: F1=%.4f, ROC-AUC=%.4f", metrics["f1"], metrics["roc_auc"])


if __name__ == "__main__":
	main()
