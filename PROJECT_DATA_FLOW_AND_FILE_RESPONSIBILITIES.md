# Stock Agent: Data Flow and File Responsibilities

This document explains exactly how this app uses data, where the data comes from, how prediction works, and what each file is responsible for.

---

## 1) Short answer (final confirmation)

Yes — the app is **dataset-driven**.

- Data source is **Yahoo Finance** via the `yfinance` package.
- Backend default period is **5 years** (`"5y"`).
- Models are trained from fetched dataset features, then used for prediction.
- Frontend currently calls backend without overriding period, so it uses backend default `5y`.

---

## 2) End-to-end pipeline

1. Frontend calls backend:
   - `GET /predict?ticker=...` (predict)
   - `POST /train?ticker=...` (force retrain)
2. Backend receives request in `app/api.py` and calls `run()` from `src/main.py`.
3. `run()` fetches market data from Yahoo Finance using ticker + period.
4. `run()` builds technical features (`MA`, `EMA`, `MACD`, `RSI`, returns, volatility, volume change).
5. If retrain is requested (or model missing), model is trained and saved in `models/`.
6. Prediction uses saved model artifact for the ticker.
7. Result JSON includes:
   - current/predicted prices
   - decision (BUY/HOLD/SELL)
   - validation metrics
   - provenance info (source, period, rows, date range)

---

## 3) Where dataset comes from

### Source
- External source: **Yahoo Finance**
- Library: `yfinance`

### Code location
- Fetch logic: `src/fetch.py` in `fetch_stock_data()`
- Call used: `yf.download(current_ticker, period=period, ...)`

### Data cleaning
- Ensures `Close` column exists.
- Handles potential multi-index columns.
- Drops missing values (`dropna`).
- Raises error if no usable rows remain.

---

## 4) Why this uses 5-year data by default

`app/api.py` defines default request params:

- `/train`: `period = request.args.get("period", "5y")`
- `/predict`: `period = request.args.get("period", "5y")`

Frontend calls `/train` and `/predict` without a `period` query parameter, so backend default `5y` is used.

---

## 5) Feature engineering (dataset -> model inputs)

In `src/features.py`, `add_features(data)` creates model features from raw price data:

- Moving averages: `MA10`, `MA20`, `MA50`
- Exponential moving averages: `EMA12`, `EMA26`
- Momentum: `MACD`, `RSI14`
- Returns: `Return1`, `Return5`
- Risk proxy: `Volatility`
- Volume behavior: `VolumeChange`

After creating features, rows with missing values are removed.

---

## 6) Training logic (how model learns)

In `src/train.py`, `train_model(data, ticker)`:

- Builds supervised targets:
  - `NextClose` (future close)
  - `FutureReturn`
  - `DecisionTarget` (SELL/HOLD/BUY by quantiles)
- Uses config-defined features (`FEATURE_COLUMNS`).
- Splits dataset time-wise by `TRAIN_SPLIT_RATIO`.
- Trains:
  - `RandomForestRegressor` for next price
  - `RandomForestClassifier` for decision class
- Calculates validation metrics (`mae`, `rmse`, `r2`, decision accuracy, etc.).
- Saves artifact with models + metadata to:
  - `models/model_<TICKER>.pkl`

So predictions come from trained model parameters learned from historical dataset, not hardcoded prices.

---

## 7) Prediction logic (how output is produced)

In `src/predict.py`, `predict_price(data, ticker)`:

- Loads trained artifact from `models/model_<TICKER>.pkl`.
- Validates required features are present.
- Uses latest feature row to run model inference.
- Produces:
  - `model_price`
  - `predicted_return`
  - `model_decision`
  - `final_price` (currently model-driven in your latest update)

If artifact is missing/invalid, backend requires training first.

---

## 8) API responsibilities

In `app/api.py`:

- `GET /health`
  - Checks server status and whether default model exists.
- `POST /train`
  - Forces retraining (`force_retrain=True`) on fetched dataset.
- `GET /predict`
  - Uses existing model unless `retrain=true` is provided.

---

## 9) Frontend responsibilities

### `frontend/src/App.jsx`
- Handles ticker input.
- `Predict` button calls `/predict`.
- `Retrain` button calls `/train`.
- Displays model outputs, confidence, metrics, provenance, and recent trend chart.

### `frontend/src/main.jsx`
- React app bootstrap entry point.

### Styles
- `frontend/src/App.css`, `frontend/src/index.css` handle UI styling only.

---

## 10) Backend/core file-by-file responsibility map

### `app/api.py`
HTTP API layer (Flask): route parsing, calling core pipeline, JSON response.

### `src/main.py`
Pipeline orchestrator: fetch -> feature engineer -> train if needed -> predict -> return result payload.

### `src/fetch.py`
Data ingestion from Yahoo Finance and cleanup.

### `src/features.py`
Feature engineering from raw OHLCV-style stock data.

### `src/train.py`
Model training + validation metrics + artifact persistence.

### `src/predict.py`
Artifact loading + inference on latest engineered features.

### `src/config.py`
Central configuration/constants:
- feature list
- training hyperparameters
- model path rules
- blending/baseline constants (some may now be legacy depending on latest predict logic)

### `src/decision.py`
Simple helper decision rule (`BUY/SELL/HOLD`) from current vs predicted price.
Currently not the main path when classifier-based decision is used.

---

## 11) Model artifacts and persistence

- Directory: `models/`
- Per ticker file: `model_<TICKER>.pkl`
- Saved using `joblib`.
- Artifact includes trained models and metadata (`trained_at`, metrics, horizon, etc.).

---

## 12) Dependencies enabling data-driven behavior

From `requirements.txt`:

- `yfinance` (dataset source)
- `pandas`, `numpy` (data processing)
- `scikit-learn` (ML models)
- `joblib` (artifact save/load)
- `flask` (API service)

---

## 13) Operational notes

- If you want prediction to always reflect newest market data + newest model, use **Retrain** before Predict.
- If you only click Predict, app may reuse an existing model artifact for that ticker.
- You can override period by passing query param (example: `period=1y`), otherwise default is `5y`.

---

## 14) Quick trust checklist (for future reading)

To verify dataset-driven behavior at any time:

1. Confirm `src/fetch.py` still uses `yf.download(...)`.
2. Confirm `src/train.py` still trains on engineered features and writes `models/model_<TICKER>.pkl`.
3. Confirm `src/predict.py` uses loaded model artifact to predict.
4. Confirm API routes default/use `period="5y"` (or your chosen period).
5. Confirm response includes provenance fields (`data_source`, `data_period`, `data_rows`, dates).

If all 5 checks pass, the app remains dataset-driven.
