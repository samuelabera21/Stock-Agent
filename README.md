
# Stock Agent 🚀

Live Demo: https://stock-agent-bn3k.vercel.app/

AI Stock Agent with a Flask backend and React frontend.

AI Stock Agent with a Flask backend and React frontend.

This project is dataset-driven: it fetches market data from Yahoo Finance (`yfinance`), engineers features, trains ML models, and predicts prices/decisions from that data.

## Project Structure

- `app/` → Flask API (`/health`, `/train`, `/predict`)
- `src/` → data fetch, features, training, prediction, config
- `frontend/` → React + Vite dashboard
- `models/` → saved model artifacts (`model_<TICKER>.pkl`)
- `PROJECT_DATA_FLOW_AND_FILE_RESPONSIBILITIES.md` → detailed technical documentation

## Requirements

- Python 3.10+
- Node.js 18+
- npm

## Quick Run (Local)

Use 2 terminals.

Terminal 1 (Backend):

```bash
cd /s/Project/python/stock-agent-project
source /c/Users/hp/anaconda3/Scripts/activate stock_agent
python -m pip install -r requirements.txt
python app/api.py
```

Terminal 2 (Frontend):

```bash
cd /s/Project/python/stock-agent-project/frontend
cp .env.example .env.local
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend health: `http://127.0.0.1:5000/health`

## 1) Backend Setup

From project root:

```bash
cd /s/Project/python/stock-agent-project
source /c/Users/hp/anaconda3/Scripts/activate stock_agent
python -m pip install -r requirements.txt
python app/api.py
```

Backend runs on: `http://127.0.0.1:5000`

## 2) Frontend Setup

Open a second terminal:

```bash
cd /s/Project/python/stock-agent-project/frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

### Frontend API configuration (safe for deploy)

For local development, create a local env file from the example:

```bash
cd /s/Project/python/stock-agent-project/frontend
cp .env.example .env.local
```

Use this in `frontend/.env.local`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:5000
```

For production (Vercel), set `VITE_API_BASE_URL` in Vercel Project Settings to your HTTPS backend URL (for example Render).

This does not change deployed behavior by itself; `.env.local` is local-only and ignored by git.

## API Endpoints

- `GET /health`
  - Health check + whether default model exists.
- `POST /train?ticker=AAPL&period=5y`
  - Force retrain model using fetched dataset.
- `GET /predict?ticker=AAPL&period=5y`
  - Predict using trained model (or retrain with `retrain=true`).

Examples:

```bash
curl "http://127.0.0.1:5000/health"
curl -X POST "http://127.0.0.1:5000/train?ticker=AAPL&period=5y"
curl "http://127.0.0.1:5000/predict?ticker=AAPL&period=5y"
```

## Is It Really Data-Driven?

Yes.

- Data source: Yahoo Finance via `yfinance` in `src/fetch.py`
- Default period: `5y` in `app/api.py`
- Training: `src/train.py` builds models from engineered dataset features
- Prediction: `src/predict.py` loads trained model artifacts and infers from latest feature row

## Notes

- Click **Retrain** in UI to rebuild model with latest fetched data.
- Click **Predict** for inference using current saved model.
- Models are saved per ticker in `models/`.
