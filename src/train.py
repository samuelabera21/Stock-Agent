from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from .config import (
        BASELINE_HARD_CUTOFF,
        BLEND_WEIGHT_WHEN_STRONGER,
        BLEND_WEIGHT_WHEN_WEAKER,
        FEATURE_COLUMNS,
        MIN_ROWS_FOR_TRAINING,
        N_ESTIMATORS,
        RANDOM_STATE,
        TARGET_HORIZON_DAYS,
        TRAIN_SPLIT_RATIO,
        model_path_for_ticker,
    )
except ImportError:
    from config import (
        BASELINE_HARD_CUTOFF,
        BLEND_WEIGHT_WHEN_STRONGER,
        BLEND_WEIGHT_WHEN_WEAKER,
        FEATURE_COLUMNS,
        MIN_ROWS_FOR_TRAINING,
        N_ESTIMATORS,
        RANDOM_STATE,
        TARGET_HORIZON_DAYS,
        TRAIN_SPLIT_RATIO,
        model_path_for_ticker,
    )


def train_model(data, ticker="AAPL"):
    missing = [column for column in FEATURE_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    dataset = data.copy()
    close = dataset["Close"]
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]

    dataset["CurrentClose"] = close
    dataset["NextClose"] = close.shift(-TARGET_HORIZON_DAYS)
    dataset["Target"] = dataset["NextClose"]
    dataset["FutureReturn"] = (dataset["NextClose"] / dataset["CurrentClose"]) - 1.0
    dataset.dropna(inplace=True)

    lower_q = float(dataset["FutureReturn"].quantile(0.33))
    upper_q = float(dataset["FutureReturn"].quantile(0.67))
    if lower_q >= upper_q:
        lower_q = float(dataset["FutureReturn"].quantile(0.30))
        upper_q = float(dataset["FutureReturn"].quantile(0.70))

    dataset["DecisionTarget"] = pd.cut(
        dataset["FutureReturn"],
        bins=[-np.inf, lower_q, upper_q, np.inf],
        labels=["SELL", "HOLD", "BUY"],
        include_lowest=True,
    ).astype(str)

    if len(dataset) < MIN_ROWS_FOR_TRAINING:
        raise ValueError(
            f"Not enough data for training. Need at least {MIN_ROWS_FOR_TRAINING} rows after feature engineering."
        )

    X = dataset[FEATURE_COLUMNS]
    y = dataset["Target"]
    y_decision = dataset["DecisionTarget"]

    split_index = max(int(len(dataset) * TRAIN_SPLIT_RATIO), 1)
    if split_index >= len(dataset):
        split_index = len(dataset) - 1

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    y_decision_train = y_decision.iloc[:split_index]
    y_decision_test = y_decision.iloc[split_index:]
    current_close_test = dataset["CurrentClose"].iloc[split_index:]
    next_close_test = dataset["NextClose"].iloc[split_index:]

    price_model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    price_model.fit(X_train, y_train.to_numpy().ravel())

    decision_model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    decision_model.fit(X_train, y_decision_train)

    pred_next_close = price_model.predict(X_test)
    pred_decision = decision_model.predict(X_test)
    actual_next_close = next_close_test.to_numpy()
    baseline_next_close = current_close_test.to_numpy()

    baseline_mae = float(mean_absolute_error(actual_next_close, baseline_next_close))
    model_mae = float(mean_absolute_error(actual_next_close, pred_next_close))
    quality_ratio = float(baseline_mae / max(model_mae, 1e-12))
    use_baseline = quality_ratio < BASELINE_HARD_CUTOFF

    if use_baseline:
        blend_weight = 0.0
    elif quality_ratio < 1.0:
        blend_weight = BLEND_WEIGHT_WHEN_WEAKER
    else:
        blend_weight = BLEND_WEIGHT_WHEN_STRONGER

    metrics = {
        "mae": model_mae,
        "rmse": float(np.sqrt(mean_squared_error(actual_next_close, pred_next_close))),
        "r2": float(r2_score(actual_next_close, pred_next_close)),
        "baseline_mae": baseline_mae,
        "quality_ratio": quality_ratio,
        "decision_accuracy": float(accuracy_score(y_decision_test, pred_decision)),
        "decision_quantiles": {
            "lower": lower_q,
            "upper": upper_q,
        },
        "target": "next_close_price",
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }

    artifact = {
        "price_model": price_model,
        "decision_model": decision_model,
        "feature_columns": FEATURE_COLUMNS,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "ticker": ticker.upper(),
        "target_horizon_days": TARGET_HORIZON_DAYS,
        "use_baseline": use_baseline,
        "blend_weight": blend_weight,
    }

    model_path = model_path_for_ticker(ticker)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)

    return artifact