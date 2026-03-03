
# Stock Agent 🚀

Live Demo: https://stock-agent-bn3k.vercel.app/

AI Stock Agent with a Flask backend and React frontend.

AI Stock Agent with a Flask backend and React frontend.

This project is dataset-driven: it fetches market data from Yahoo Finance (`yfinance`), engineers features, trains ML models, and predicts prices/decisions from that data.

## Project Structure

- `app/` → Flask API (`/health`, `/train`, `/predict`)
- `src/` → data fetch, features, training, prediction, config
- `frontend/` → React + Vite dashboard
- `models/` → saved model artifacts (`model_<TICKER>_<PERIOD>.pkl`)
- `PROJECT_DATA_FLOW_AND_FILE_RESPONSIBILITIES.md` → detailed technical documentation

## Requirements

- Python 3.10+
- Node.js 18+
- npm

## Quick Run (Local)

Use 2 terminals.

Terminal 1 (Backend):

```bash
cd /s/Project/Stock-Agent
source /c/Users/hp/anaconda3/Scripts/activate stock_agent
python -m pip install -r requirements.txt
python app/api.py
```

Terminal 2 (Frontend):

```bash
cd /s/Project/Stock-Agent/frontend
cp .env.example .env.local
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend health: `http://127.0.0.1:5000/health`

## Run + View Result (Local)

1. Start backend:

```bash
cd /s/Project/Stock-Agent
source /c/Users/hp/anaconda3/Scripts/activate stock_agent
python app/api.py
```

2. Start frontend (second terminal):

```bash
cd /s/Project/Stock-Agent/frontend
cp .env.example .env.local
npm install
npm run dev
```

3. Open `http://localhost:5173`
4. In UI, enter ticker (for example `AAPL`) and click **Retrain** once.
5. Then click **Predict** multiple times.
  - First call may be slower.
  - Repeated calls within cache TTL are faster (response includes `"cached": true`).

## Frontend API configuration (safe for deploy)

For local development, create a local env file from the example:

```bash
cd /s/Project/Stock-Agent/frontend
cp .env.example .env.local
```

Use this in `frontend/.env.local`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:5000
VITE_API_TIMEOUT_MS=45000
```

For production (Vercel), set `VITE_API_BASE_URL` in Vercel Project Settings to your HTTPS backend URL (for example Render).

This does not change deployed behavior by itself; `.env.local` is local-only and ignored by git.

## Update Existing Deployment (Exact Steps)

### A) Update backend on Render

1. Push latest code to your GitHub repo.
2. Open Render Dashboard → your `stock-agent-api` service.
3. Go to **Environment** and set (or verify):
  - `DEFAULT_TRAIN_PERIOD=5y`
  - `DEFAULT_PREDICT_PERIOD=1y`
  - `YFINANCE_FETCH_TIMEOUT_SECONDS=12`
  - `PREDICT_CACHE_TTL_SECONDS=60`
4. Click **Save Changes**.
5. Trigger deploy (**Manual Deploy** → **Deploy latest commit**) or wait for auto deploy.
6. Verify backend:
  - `GET https://<your-render-domain>/health`
  - `POST https://<your-render-domain>/train?ticker=AAPL&period=5y`
  - `GET https://<your-render-domain>/predict?ticker=AAPL&period=1y`

### B) Update frontend on Vercel

1. Open Vercel Dashboard → your project (`stock-agent-bn3k`).
2. Go to **Settings** → **Environment Variables**.
3. Set (or verify):
  - `VITE_API_BASE_URL=https://<your-render-domain>`
  - `VITE_API_TIMEOUT_MS=45000`
4. Save and redeploy:
  - **Deployments** tab → open latest deployment → **Redeploy**
  - Or push latest commit and let Vercel auto-deploy.
5. Open live URL (`https://stock-agent-bn3k.vercel.app/`) and test:
  - Click **Retrain** once for ticker.
  - Click **Predict**; repeated predicts should respond faster.

## API Endpoints

- `GET /health`
  - Health check + whether default model exists.
- `GET|POST /train?ticker=AAPL&period=5y`
  - Force retrain model using fetched dataset.
- `GET /predict?ticker=AAPL&period=1y`
  - Predict using trained model.
  - If model artifact is missing (for example after a redeploy), API auto-trains once and then returns prediction.
  - You can still force refresh with `retrain=true`.

Examples:

```bash
curl "http://127.0.0.1:5000/health"
curl -X POST "http://127.0.0.1:5000/train?ticker=AAPL&period=5y"
curl "http://127.0.0.1:5000/predict?ticker=AAPL&period=1y"
```

## Is It Really Data-Driven?

Yes.

- Data source: Yahoo Finance via `yfinance` in `src/fetch.py`
- Default train period: `5y` and default predict period: `1y` in `app/api.py`
- Training: `src/train.py` builds models from engineered dataset features
- Prediction: `src/predict.py` loads trained model artifacts and infers from latest feature row
- Final decision is derived from predicted return against training quantile thresholds (dataset-driven), with classifier agreement used as secondary confirmation.

## Notes

- Click **Retrain** in UI to rebuild model with latest fetched data.
- Click **Predict** for inference using current saved model.
- Models are saved per ticker in `models/`.
- Optional env vars:
  - Backend: `DEFAULT_TRAIN_PERIOD`, `DEFAULT_PREDICT_PERIOD`, `YFINANCE_FETCH_TIMEOUT_SECONDS`, `PREDICT_CACHE_TTL_SECONDS`
  - Frontend: `VITE_API_TIMEOUT_MS`
