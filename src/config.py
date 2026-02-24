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
N_ESTIMATORS = 500
MIN_ROWS_FOR_TRAINING = 120
TARGET_HORIZON_DAYS = 1

BASELINE_HARD_CUTOFF = 0.6
BASELINE_BLEND_WEIGHT = 0.15
BLEND_WEIGHT_WHEN_WEAKER = 0.35
BLEND_WEIGHT_WHEN_STRONGER = 0.8


def model_path_for_ticker(ticker: str) -> Path:
	normalized = (ticker or "AAPL").upper().strip().replace("/", "_")
	return MODELS_DIR / f"model_{normalized}.pkl"