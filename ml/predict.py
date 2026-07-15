from __future__ import annotations

import argparse
import json
from typing import Any

from scripts.pipeline_utils import load_best_model
from scripts.preprocessing import prepare_prediction_frame


def predict_three_point(
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
	playerName: str = "Unknown",
) -> dict[str, Any]:
	model = load_best_model()
	frame = prepare_prediction_frame(
		shotDistance=shotDistance,
		shotZone=shotZone,
		period=period,
		minutesRemaining=minutesRemaining,
		secondsRemaining=secondsRemaining,
		shotClock=shotClock,
		defenderDistance=defenderDistance,
		dribbles=dribbles,
		touchTime=touchTime,
		locationX=locationX,
		locationY=locationY,
		playerName=playerName,
	)
	probability = float(model.predict_proba(frame)[0, 1])
	prediction = "Made" if probability >= 0.5 else "Missed"
	return {"prediction": prediction, "probability": probability}


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Predict whether an NBA three-point shot is made or missed.")
	parser.add_argument("--shotDistance", type=float, required=True)
	parser.add_argument("--shotZone", type=str, required=True)
	parser.add_argument("--period", type=int, required=True)
	parser.add_argument("--minutesRemaining", type=float, required=True)
	parser.add_argument("--secondsRemaining", type=float, required=True)
	parser.add_argument("--shotClock", type=float, required=True)
	parser.add_argument("--defenderDistance", type=float, required=True)
	parser.add_argument("--dribbles", type=float, required=True)
	parser.add_argument("--touchTime", type=float, required=True)
	parser.add_argument("--locationX", type=float, required=True)
	parser.add_argument("--locationY", type=float, required=True)
	parser.add_argument("--playerName", type=str, default="Unknown")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	result = predict_three_point(
		shotDistance=args.shotDistance,
		shotZone=args.shotZone,
		period=args.period,
		minutesRemaining=args.minutesRemaining,
		secondsRemaining=args.secondsRemaining,
		shotClock=args.shotClock,
		defenderDistance=args.defenderDistance,
		dribbles=args.dribbles,
		touchTime=args.touchTime,
		locationX=args.locationX,
		locationY=args.locationY,
		playerName=args.playerName,
	)
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
