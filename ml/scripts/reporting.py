from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from scripts.config import REPORTS_DIR
from scripts.utils import write_text_file


def create_model_report(
	dataset_summary: dict[str, Any],
	feature_statistics: pd.DataFrame,
	model_comparison: pd.DataFrame,
	best_model_name: str,
	feature_importance: pd.DataFrame,
	output_path: str | Path,
) -> Path:
	lines: list[str] = ["NBA 3-Point Shot Prediction and Analysis System", ""]
	lines.append("Dataset Summary")
	for key, value in dataset_summary.items():
		lines.append(f"- {key}: {value}")
	lines.append("")
	lines.append("Feature Statistics")
	lines.append(feature_statistics.to_string(index=False))
	lines.append("")
	lines.append("Model Comparison")
	lines.append(model_comparison.to_string(index=False))
	lines.append("")
	lines.append(f"Best Model Selected: {best_model_name}")
	lines.append("")
	lines.append("Feature Importance Ranking")
	lines.append(feature_importance.head(15).to_string(index=False))

	output_file = Path(output_path)
	write_text_file(output_file, lines)
	return output_file
