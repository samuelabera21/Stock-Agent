import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "model.pkl"

FEATURE_COLUMNS = [
	"MA10",
	"MA20",
	"MA50",
	"EMA12",
	"EMA26",
	"MACD",
	"RSI14",
	"Return1",
	"Return5",
	"Volatility",
	"VolumeChange",
]

TRAIN_SPLIT_RATIO = 0.8
RANDOM_STATE = 42
N_ESTIMATORS = int(os.getenv("N_ESTIMATORS", "120"))
MIN_ROWS_FOR_TRAINING = 120
TARGET_HORIZON_DAYS = 1
DEFAULT_TRAIN_PERIOD = os.getenv("DEFAULT_TRAIN_PERIOD", "5y")
DEFAULT_PREDICT_PERIOD = os.getenv("DEFAULT_PREDICT_PERIOD", "1y")
YFINANCE_FETCH_TIMEOUT_SECONDS = float(os.getenv("YFINANCE_FETCH_TIMEOUT_SECONDS", "12"))

BASELINE_HARD_CUTOFF = 0.6
BASELINE_BLEND_WEIGHT = 0.15
BLEND_WEIGHT_WHEN_WEAKER = 0.35
BLEND_WEIGHT_WHEN_STRONGER = 0.8


def model_path_for_ticker(ticker: str, period: str | None = None) -> Path:
	normalized_ticker = (ticker or "AAPL").upper().strip().replace("/", "_")
	if period is None:
		return MODELS_DIR / f"model_{normalized_ticker}.pkl"

	normalized_period = str(period).strip().replace("/", "_").replace(" ", "")
	return MODELS_DIR / f"model_{normalized_ticker}_{normalized_period}.pkl"