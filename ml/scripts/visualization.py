from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from scripts.config import PLOTS_DIR

sns.set_theme(style="whitegrid")


def save_correlation_heatmap(df: pd.DataFrame, output_path: str | Path) -> Path:
	numeric_df = df.select_dtypes(include=[np.number])
	correlation = numeric_df.corr(numeric_only=True)

	plt.figure(figsize=(12, 10))
	sns.heatmap(correlation, cmap="coolwarm", center=0, square=False)
	plt.title("Correlation Heatmap")
	plt.tight_layout()

	output_file = Path(output_path)
	output_file.parent.mkdir(parents=True, exist_ok=True)
	plt.savefig(output_file, dpi=200, bbox_inches="tight")
	plt.close()
	return output_file


def save_confusion_matrix(confusion: np.ndarray, output_path: str | Path) -> Path:
	plt.figure(figsize=(7, 6))
	sns.heatmap(confusion, annot=True, fmt="d", cmap="Blues", cbar=False)
	plt.xlabel("Predicted")
	plt.ylabel("Actual")
	plt.title("Confusion Matrix")
	plt.tight_layout()

	output_file = Path(output_path)
	output_file.parent.mkdir(parents=True, exist_ok=True)
	plt.savefig(output_file, dpi=200, bbox_inches="tight")
	plt.close()
	return output_file


def save_roc_curve(fpr: np.ndarray, tpr: np.ndarray, roc_auc: float, output_path: str | Path) -> Path:
	plt.figure(figsize=(7, 6))
	plt.plot(fpr, tpr, label=f"ROC-AUC = {roc_auc:.3f}", linewidth=2)
	plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
	plt.xlabel("False Positive Rate")
	plt.ylabel("True Positive Rate")
	plt.title("ROC Curve")
	plt.legend(loc="lower right")
	plt.tight_layout()

	output_file = Path(output_path)
	output_file.parent.mkdir(parents=True, exist_ok=True)
	plt.savefig(output_file, dpi=200, bbox_inches="tight")
	plt.close()
	return output_file


def save_feature_importance_plot(feature_importance: pd.DataFrame, output_path: str | Path, top_n: int = 15) -> Path:
	top_features = feature_importance.head(top_n).iloc[::-1]
	plt.figure(figsize=(10, 7))
	plt.barh(top_features["feature"], top_features["importance"], color="#1f77b4")
	plt.xlabel("Importance")
	plt.title(f"Top {top_n} Feature Importances")
	plt.tight_layout()

	output_file = Path(output_path)
	output_file.parent.mkdir(parents=True, exist_ok=True)
	plt.savefig(output_file, dpi=200, bbox_inches="tight")
	plt.close()
	return output_file
