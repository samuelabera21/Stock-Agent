
# Stock Agent

AI Stock Agent with a Flask backend and React frontend.

Live frontend: https://stock-agent-bn3k.vercel.app/
Live backend: https://stock-agent-api-5rcn.onrender.com

## What this app does

This app is dataset-driven end to end:

1. Downloads real market data from Yahoo Finance (`yfinance`).
2. Builds technical features from that dataset.
3. Trains models per ticker/period.
4. Predicts next price.
5. Produces `BUY` / `SELL` / `HOLD` from learned quantile thresholds.

## Current health status (verified)

The current codebase has been validated with:

- Static checks: no Python errors in `src/` and `app/`.
- Runtime pipeline: `fetch -> feature -> train -> predict` executes successfully on live data.
- API checks: `/health` and `/predict` return `200` via Flask test client.
- Decision behavior: not stuck on hardcoded `HOLD`; live run produced `BUY` with real data.

## Project structure

- `app/api.py`: Flask API (`/`, `/health`, `/train`, `/predict`) + in-memory prediction cache.
- `src/fetch.py`: Yahoo Finance data retrieval + ticker fallback handling.
- `src/features.py`: feature engineering (MA, EMA, MACD, RSI, returns, volatility, volume change).
- `src/train.py`: model training (regressor + classifier), metrics, quantile threshold learning.
- `src/predict.py`: artifact loading, prediction, baseline blending, final decision logic.
- `src/main.py`: orchestrates pipeline and returns API-ready response payload.
- `frontend/src/App.jsx`: dashboard UI, API calls, and result display.
- `models/`: persisted model artifacts, one file per ticker/period.

## Decision logic (where BUY / SELL / HOLD comes from)

Decision logic is model-driven and dataset-derived, not hardcoded.

### Training stage (`src/train.py`)

- Computes `FutureReturn = (NextClose / CurrentClose) - 1` from dataset rows.
- Learns quantile thresholds from actual data distribution:
  - lower quantile (around 33%)
  - upper quantile (around 67%)
- Creates training labels:
  - `FutureReturn <= lower_q` -> `SELL`
  - `FutureReturn >= upper_q` -> `BUY`
  - otherwise -> `HOLD`
- Trains:
  - `RandomForestRegressor` for price
  - `RandomForestClassifier` for class confirmation
- Saves artifact with metrics, quantiles, baseline flags, and blend weight.

### Prediction stage (`src/predict.py`)

- Loads artifact for requested ticker/period.
- Computes:
  - `model_price` and `model_predicted_return`
  - `final_price` using blend/baseline safety logic
  - `predicted_return` from `final_price`
- Uses `decision_return` (model directional return) against learned `lower_q`/`upper_q` to produce quantile decision.
- If classifier agrees, marks source as `regression+classifier`; otherwise uses `regression-quantile`.

## API response highlights

`GET /predict?ticker=AAPL&period=1y` returns fields including:

- Prices: `current_price`, `model_price`, `predicted_price`
- Returns: `model_predicted_return`, `decision_return`, `predicted_return`
- Decision: `decision`, `decision_source`, `classifier_decision`, `decision_thresholds`
- Safety/meta: `used_baseline`, `blend_weight`, `confidence`
- Data provenance: `data_source`, `data_period`, `data_rows`, `data_start`, `data_end`
- Training/meta: `metrics`, `trained_at`, `target_horizon_days`, `model_file`

## Local development

Requirements:

- Python 3.10+
- Node.js 18+

### Backend

```bash
cd /s/Project/Stock-Agent
python -m pip install -r requirements.txt
python app/api.py
```

### Frontend

```bash
cd /s/Project/Stock-Agent/frontend
cp .env.example .env.local
npm install
npm run dev
```

Use in `frontend/.env.local`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:5000
VITE_API_TIMEOUT_MS=120000
```

## Deployment (Render + Vercel)

### Render backend (`stock-agent-api`)

Required environment variables:

- `DEFAULT_TRAIN_PERIOD=5y`
- `DEFAULT_PREDICT_PERIOD=1y`
- `YFINANCE_FETCH_TIMEOUT_SECONDS=12`
- `PREDICT_CACHE_TTL_SECONDS=60`

Deploy steps:

1. Push to GitHub `main`.
2. Render -> service -> **Manual Deploy** -> **Deploy latest commit**.
3. Verify:
   - `GET https://stock-agent-api-5rcn.onrender.com/health`
   - `GET https://stock-agent-api-5rcn.onrender.com/predict?ticker=AAPL&period=1y`

### Vercel frontend (`stock-agent-bn3k`)

Required environment variables:

- `VITE_API_BASE_URL=https://stock-agent-api-5rcn.onrender.com`
- `VITE_API_TIMEOUT_MS=120000`

Deploy steps:

1. Vercel -> project -> **Settings** -> **Environment Variables**.
2. Add vars for `Production` (and `Preview` if needed).
3. Redeploy latest build.

## Common behavior notes

- First `predict` for a ticker may be slower due to model load or auto-train.
- Render free tier may cold-start (delay up to ~50s).
- Prediction caching is enabled by backend TTL.
- If predictions look stale, use `retrain=true` or call `/train`.

## Troubleshooting

- Frontend shows `API is not configured`:
  - Missing `VITE_API_BASE_URL` in Vercel env vars.
- Frequent `HOLD` decisions:
  - Retrain model for ticker (`/train`) after code updates.
  - Check `decision_thresholds`, `model_predicted_return`, and `decision_return` in response.
- `No data returned for ticker`:
  - Verify symbol, period, and Yahoo availability.

## License

Internal project (no license file specified).
