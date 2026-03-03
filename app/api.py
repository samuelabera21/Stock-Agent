import os
import sys
import time
from copy import deepcopy
from pathlib import Path
from threading import Lock

from flask import Flask, jsonify, request
from flask_cors import CORS


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.main import run
from src.config import DEFAULT_PREDICT_PERIOD, DEFAULT_TRAIN_PERIOD, model_path_for_ticker


app = Flask(__name__)
CORS(app)


PREDICT_CACHE_TTL_SECONDS = int(os.getenv("PREDICT_CACHE_TTL_SECONDS", "60"))
PREDICT_CACHE = {}
PREDICT_CACHE_LOCK = Lock()


def _cache_key(ticker: str, period: str):
    return f"{(ticker or 'AAPL').upper().strip()}|{(period or DEFAULT_PREDICT_PERIOD).strip()}"


def _get_cached_prediction(ticker: str, period: str):
    key = _cache_key(ticker, period)
    now = time.time()

    with PREDICT_CACHE_LOCK:
        entry = PREDICT_CACHE.get(key)
        if not entry:
            return None

        expires_at = float(entry.get("expires_at", 0))
        if now >= expires_at:
            PREDICT_CACHE.pop(key, None)
            return None

        cached_result = deepcopy(entry.get("result", {}))

    if not cached_result:
        return None

    cached_result["cached"] = True
    cached_result["cache_ttl_seconds"] = PREDICT_CACHE_TTL_SECONDS
    return cached_result


def _set_cached_prediction(ticker: str, period: str, result: dict):
    key = _cache_key(ticker, period)
    now = time.time()

    with PREDICT_CACHE_LOCK:
        PREDICT_CACHE[key] = {
            "expires_at": now + PREDICT_CACHE_TTL_SECONDS,
            "result": deepcopy(result),
        }


def _invalidate_cache_for_ticker(ticker: str):
    normalized = (ticker or "AAPL").upper().strip()
    with PREDICT_CACHE_LOCK:
        keys_to_remove = [cache_key for cache_key in PREDICT_CACHE.keys() if cache_key.startswith(f"{normalized}|")]
        for cache_key in keys_to_remove:
            PREDICT_CACHE.pop(cache_key, None)


@app.get("/")
def index():
    return jsonify(
        {
            "name": "stock-agent-api",
            "status": "ok",
            "endpoints": ["/health", "/train", "/predict"],
        }
    )


@app.get("/health")
def health():
    default_model = model_path_for_ticker("AAPL", period=DEFAULT_PREDICT_PERIOD)
    return jsonify(
        {
            "status": "ok",
            "model_ready": default_model.exists(),
        }
    )


@app.route("/train", methods=["GET", "POST"])
def train():
    ticker = request.args.get("ticker", "AAPL")
    period = request.args.get("period", DEFAULT_TRAIN_PERIOD)

    try:
        result = run(ticker=ticker, period=period, force_retrain=True)
        _invalidate_cache_for_ticker(ticker)
        result["cached"] = False
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@app.get("/predict")
def predict():
    ticker = request.args.get("ticker", "AAPL")
    period = request.args.get("period", DEFAULT_PREDICT_PERIOD)
    retrain = request.args.get("retrain", "false").lower() == "true"

    auto_trained = False

    try:
        if not retrain and PREDICT_CACHE_TTL_SECONDS > 0:
            cached = _get_cached_prediction(ticker=ticker, period=period)
            if cached is not None:
                return jsonify(cached)

        try:
            result = run(ticker=ticker, period=period, force_retrain=retrain)
        except FileNotFoundError:
            result = run(ticker=ticker, period=period, force_retrain=True)
            auto_trained = True

        if retrain or auto_trained:
            _invalidate_cache_for_ticker(ticker)

        result["cached"] = False
        result["cache_ttl_seconds"] = PREDICT_CACHE_TTL_SECONDS
        result["auto_trained"] = auto_trained

        if not retrain and PREDICT_CACHE_TTL_SECONDS > 0:
            _set_cached_prediction(ticker=ticker, period=period, result=result)

        return jsonify(result)
    except Exception as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)