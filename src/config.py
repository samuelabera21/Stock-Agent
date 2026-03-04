import os
from pathlib import Path


# Build an absolute path to this repository root (portable across Windows/Linux/macOS).
# __file__ = current file location, resolve() = absolute path, parent.parent = move from src/config.py to project root.
BASE_DIR = Path(__file__).resolve().parent.parent
# Keep all trained model artifacts in one dedicated folder under project root.
MODELS_DIR = BASE_DIR / "models"
# Default single-model path (legacy/general fallback path).
MODEL_PATH = MODELS_DIR / "model.pkl"

# Ordered list of engineered input features used by both training and inference.
# Keeping this in config guarantees train/predict use the exact same feature schema.
FEATURE_COLUMNS = [
	# 10-day simple moving average: short-term trend smoother.
	"MA10",
	# 20-day simple moving average: medium short-term trend.
	"MA20",
	# 50-day simple moving average: broader trend context.
	"MA50",
	# 12-day exponential moving average: reacts faster to recent moves.
	"EMA12",
	# 26-day exponential moving average: slower EMA for momentum comparison.
	"EMA26",
	# Momentum signal: EMA12 - EMA26.
	"MACD",
	# Relative Strength Index (14): overbought/oversold oscillator.
	"RSI14",
	# 1-day return: very short-term directional signal.
	"Return1",
	# 5-day return: short/medium directional signal.
	"Return5",
	# Recent realized volatility: uncertainty/risk signal.
	"Volatility",
	# Trading volume change: participation/liquidity activity signal.
	"VolumeChange",
]

# Train/test split for time-ordered data (80% train, 20% test).
TRAIN_SPLIT_RATIO = 0.8
# Fixed random seed for reproducible model training behavior.
RANDOM_STATE = 42
# Number of trees in RandomForest; read from environment for production tuning without code edits.
N_ESTIMATORS = int(os.getenv("N_ESTIMATORS", "120"))
# Minimum number of rows required before allowing training (guards against tiny/unstable datasets).
MIN_ROWS_FOR_TRAINING = 120
# Forecast horizon in days (1 means predict next trading day's close).
TARGET_HORIZON_DAYS = 1
# Data period used when explicitly training (environment-overridable for flexible deployments).
DEFAULT_TRAIN_PERIOD = os.getenv("DEFAULT_TRAIN_PERIOD", "6mo")
# Data period used for regular prediction requests (can be lighter than training period).
DEFAULT_PREDICT_PERIOD = os.getenv("DEFAULT_PREDICT_PERIOD", "1y")
# Maximum allowed wait time for Yahoo Finance fetches to prevent hanging requests.
YFINANCE_FETCH_TIMEOUT_SECONDS = float(os.getenv("YFINANCE_FETCH_TIMEOUT_SECONDS", "12"))

# If model quality ratio is below this threshold, system uses stronger baseline fallback behavior.
BASELINE_HARD_CUTOFF = 0.6
# Blend weight for baseline path when quality is poor (more conservative output).
BASELINE_BLEND_WEIGHT = 0.15
# Blend weight when model is weaker than baseline but still usable.
BLEND_WEIGHT_WHEN_WEAKER = 0.35
# Blend weight when model is stronger and trusted more.
BLEND_WEIGHT_WHEN_STRONGER = 0.8


def model_path_for_ticker(ticker: str, period: str | None = None) -> Path:
	# Normalize ticker so storage keys are consistent and safe for filenames.
	normalized_ticker = (ticker or "AAPL").upper().strip().replace("/", "_")
	# If no period is provided, keep backward-compatible filename format.
	if period is None:
		return MODELS_DIR / f"model_{normalized_ticker}.pkl"

	# Normalize period to avoid invalid path characters and accidental whitespace mismatches.
	normalized_period = str(period).strip().replace("/", "_").replace(" ", "")
	# Return period-specific model path so each ticker+period has its own artifact.
	return MODELS_DIR / f"model_{normalized_ticker}_{normalized_period}.pkl"