# AI Stock Agent — Full End-to-End Process (Presentation Version)

This diagram shows exactly how the app works from UI request to training, artifact storage (`.pkl`), prediction, and final decision.

```mermaid
flowchart TD
    A[User enters ticker in frontend\nfrontend/src/App.jsx] --> B[Call backend API\napp/api.py -> /predict or /train]

    B --> C{Endpoint}

    %% ================= TRAIN FLOW =================
    C -->|/train| T1[Read query params\nticker, period\nDefault period from config: 5y]
    T1 --> T2[Pipeline entry\nsrc/main.py -> run(ticker, period, force_retrain=True)]
    T2 --> T3[Fetch OHLCV data\nsrc/fetch.py\nProvider: yfinance]
    T3 --> T4[Feature engineering\nsrc/features.py\nMA/EMA/MACD/RSI/Return/Volatility/VolumeChange]
    T4 --> T5[Training step\nsrc/train.py]

    T5 --> T6[Build targets\nCurrentClose, NextClose, Target, FutureReturn, DecisionTarget]
    T6 --> T7[Row cleanup\ndropna() removes warmup rows from rolling windows + horizon shift rows]
    T7 --> T8{Rows >= MIN_ROWS_FOR_TRAINING?\nconfig: 120}
    T8 -->|No| T9[Raise error\nNot enough data]
    T8 -->|Yes| T10[Train/Test split\nconfig TRAIN_SPLIT_RATIO = 0.8\ntrain_rows = floor(usable_rows*0.8)\ntest_rows = usable_rows-train_rows]

    T10 --> T11[Train regressor + classifier\nRandomForestRegressor + RandomForestClassifier\nconfig: N_ESTIMATORS, RANDOM_STATE]
    T11 --> T12[Evaluate model vs baseline\nMAE/RMSE/R2 + decision_accuracy + quality_ratio]
    T12 --> T13[Create artifact dict\nmodels + metrics + feature_columns + metadata]
    T13 --> T14[Save .pkl\njoblib.dump(...)\nPath from src/config.py model_path_for_ticker\nmodels/model_<TICKER>_<PERIOD>.pkl]
    T14 --> T15[Return JSON\ntrained_at, rows, metrics, decision info]

    %% ================= PREDICT FLOW =================
    C -->|/predict| P1[Read query params\nticker, period, retrain\nDefault period from config: 1y]
    P1 --> P2[Pipeline entry\nsrc/main.py -> run(ticker, period, force_retrain=retrain)]
    P2 --> P3[Fetch latest data\nsrc/fetch.py\nfor requested period]
    P3 --> P4[Feature engineering\nsrc/features.py\nMUST match training schema]
    P4 --> P5[Load artifact\nsrc/predict.py -> load_artifact(...)\njoblib.load(.pkl)]

    P5 --> P6{Artifact exists and period matches?}
    P6 -->|No| P7[Model-not-trained error\nor retrain path]
    P7 --> T2
    P6 -->|Yes| P8[Use latest feature row\nX_latest = data[feature_columns].iloc[-1:]]

    P8 --> P9[Regressor predicts raw next value\nprice_model.predict(X_latest)]
    P9 --> P10[Normalize output to model_price\n(next_close_price target or return target)]
    P10 --> P11[Compute model_predicted_return]
    P11 --> P12[Apply blend logic\nuse_baseline + blend_weight\nfinal_price = w*model_price + (1-w)*current_price]
    P12 --> P13[Decision thresholds\nfrom artifact metrics decision_quantiles\nlower/upper]
    P13 --> P14[Quantile decision\nSELL / HOLD / BUY]
    P14 --> P15[Classifier second opinion\n(if decision_model exists)]
    P15 --> P16[Decision fusion\nconsensus => regression+classifier\nelse => regression-quantile]
    P16 --> P17[Confidence from quality_ratio\nhigh/medium/low]
    P17 --> P18[Return prediction JSON\nprice, return, decision, confidence, thresholds]
    P18 --> P19[Frontend render result cards\nfrontend/src/App.jsx]

    %% ================= PERIOD / ROW NOTES =================
    N1[Period facts\nTrain default: 5y\nPredict default: 1y\nCan override via query param ?period=...]
    N2[Row facts\nRaw rows depend on ticker and trading days\nApprox daily bars ~250 per year\nUsable rows are reduced by feature windows + shift + dropna]

    T1 -. uses .-> N1
    P1 -. uses .-> N1
    T7 -. explains .-> N2

    style T14 fill:#1f4d2e,stroke:#2ecc71,color:#ffffff
    style P5 fill:#1f3f5b,stroke:#4db3ff,color:#ffffff
    style P16 fill:#5a3b1a,stroke:#f5b041,color:#ffffff
    style P18 fill:#2b1f4d,stroke:#a569bd,color:#ffffff
```

## How to download/export this for class

### Option 1 (Fastest): PNG/SVG export via Mermaid Live
1. Open `AI_AGENT_FULL_PROCESS_DIAGRAM.md`.
2. Copy only the Mermaid block content (from `flowchart TD` down).
3. Go to https://mermaid.live
4. Paste the diagram.
5. Click **Export** -> choose **PNG** or **SVG**.

### Option 2: PDF from VS Code
1. Open this markdown file preview.
2. Use browser/preview print: **Ctrl+P**.
3. Save as **PDF**.

### Option 3: Screenshot
1. Open markdown preview full-screen.
2. Use Windows Snipping Tool.
3. Save as image.
