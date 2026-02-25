import os
import sys
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.main import run
from src.config import model_path_for_ticker


app = Flask(__name__)
CORS(app)


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
    default_model = model_path_for_ticker("AAPL")
    return jsonify(
        {
            "status": "ok",
            "model_ready": default_model.exists(),
        }
    )


@app.post("/train")
def train():
    ticker = request.args.get("ticker", "AAPL")
    period = request.args.get("period", "5y")

    try:
        result = run(ticker=ticker, period=period, force_retrain=True)
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@app.get("/predict")
def predict():
    ticker = request.args.get("ticker", "AAPL")
    period = request.args.get("period", "5y")
    retrain = request.args.get("retrain", "false").lower() == "true"

    try:
        result = run(ticker=ticker, period=period, force_retrain=retrain)
        return jsonify(result)
    except FileNotFoundError:
        return jsonify({"error": "Model not trained yet. Call /train first."}), 400
    except Exception as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)