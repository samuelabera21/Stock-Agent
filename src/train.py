from datetime import datetime, timezone  # datetime gives current timestamp; timezone lets us store it in UTC safely.

import joblib  # Used to save/load trained model artifacts to/from disk.
import numpy as np  # Fast numerical utilities (inf, sqrt, array math).
import pandas as pd  # DataFrame operations (cut, columns, slicing, labels).
from sklearn.ensemble import RandomForestClassifier  # Predicts categorical actions: BUY/HOLD/SELL.
from sklearn.ensemble import RandomForestRegressor  # Predicts numeric value: next close price.
from sklearn.metrics import accuracy_score  # Measures classifier correctness on test set.
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score  # Core regression quality metrics.

try:
    # Package-style import (works when src is used as a Python package/module).
    from .config import (
        BASELINE_BLEND_WEIGHT,
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
    # Script-style fallback import (works when running this file directly).
    from config import (
        BASELINE_BLEND_WEIGHT,
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


def train_model(data, ticker="AAPL", period="5y"):
    # data   -> engineered market dataframe (must already contain FEATURE_COLUMNS + Close).
    # ticker -> model identity key (AAPL, MSFT, etc.) for saving/loading the correct artifact.
    # period -> training window identity (1y, 5y, etc.), also used in artifact path/versioning.

    # Build a list of required features that are missing from the incoming dataframe.
    missing = [column for column in FEATURE_COLUMNS if column not in data.columns]

    # Stop early with a clear error if any required feature is missing.
    # This prevents hidden failures later during model fitting.
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    # Copy input so training logic does not mutate the original object used elsewhere.
    dataset = data.copy()

    # Extract Close prices (the base signal used to build future targets).
    close = dataset["Close"]

    # Defensive normalization: if Close arrives as 2D, flatten to 1D series.
    # Some providers/libs occasionally return DataFrame-shaped columns.
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]

    # Save today's close explicitly as CurrentClose.
    # This becomes the baseline prediction (tomorrow == today) in evaluation.
    dataset["CurrentClose"] = close

    # Create supervised target by shifting Close upward in time.
    # Example with horizon=1: row t gets Close from row t+1 as NextClose.
    dataset["NextClose"] = close.shift(-TARGET_HORIZON_DAYS)

    # Explicit alias for regression target (predict absolute next close price).
    dataset["Target"] = dataset["NextClose"]

    # Convert future movement into return form.
    # Positive return => price expected to rise; negative => expected to fall.
    dataset["FutureReturn"] = (dataset["NextClose"] / dataset["CurrentClose"]) - 1.0

    # Remove rows made invalid by shifting/rolling edges (typically tail rows).
    dataset.dropna(inplace=True)

    # Learn adaptive decision thresholds from this dataset's own return distribution.
    # 0.33/0.67 quantiles roughly divide history into SELL, HOLD, BUY regions.
    lower_q = float(dataset["FutureReturn"].quantile(0.33))
    upper_q = float(dataset["FutureReturn"].quantile(0.67))

    # Safety guard for degenerate/flat datasets where quantiles can collapse.
    # If lower >= upper, widen the band to 0.30/0.70.
    if lower_q >= upper_q:
        lower_q = float(dataset["FutureReturn"].quantile(0.30))
        upper_q = float(dataset["FutureReturn"].quantile(0.70))

    # Convert numeric future return into class labels used by the classifier.
    # bins: (-inf, lower_q] => SELL, (lower_q, upper_q] => HOLD, (upper_q, inf) => BUY.
    dataset["DecisionTarget"] = pd.cut(
        dataset["FutureReturn"],
        bins=[-np.inf, lower_q, upper_q, np.inf],
        labels=["SELL", "HOLD", "BUY"],
        include_lowest=True,
    ).astype(str)

    # Ensure we have enough usable rows after feature engineering and shifting.
    # Too few rows produce unstable models and misleading metrics.
    if len(dataset) < MIN_ROWS_FOR_TRAINING:
        raise ValueError(
            f"Not enough data for training. Need at least {MIN_ROWS_FOR_TRAINING} rows after feature engineering."
        )

    # X          = model input matrix (all configured engineered features).
    # y          = numeric target for regressor (next close price).
    # y_decision = categorical target for classifier (BUY/HOLD/SELL).
    X = dataset[FEATURE_COLUMNS]
    y = dataset["Target"]
    y_decision = dataset["DecisionTarget"]

    # Time-aware split index: keep chronology (past for training, future for testing).
    # No shuffling because stock time series must preserve temporal order.
    split_index = max(int(len(dataset) * TRAIN_SPLIT_RATIO), 1)

    # Ensure test set is non-empty; metrics require at least one test row.
    if split_index >= len(dataset):
        split_index = len(dataset) - 1

    # Feature split.
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]

    # Regression-target split.
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # Classification-target split.
    y_decision_train = y_decision.iloc[:split_index]
    y_decision_test = y_decision.iloc[split_index:]

    # Keep current/next close in test window for baseline-vs-model comparison.
    current_close_test = dataset["CurrentClose"].iloc[split_index:]
    next_close_test = dataset["NextClose"].iloc[split_index:]

    # Build regression model that predicts next close price.
    # n_estimators controls number of trees.
    # random_state ensures reproducibility.
    # n_jobs=1 keeps behavior deterministic across machines/environments.
    price_model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )

    # Fit regressor using training features and 1D numeric target.
    # ravel() flattens to shape sklearn expects.
    price_model.fit(X_train, y_train.to_numpy().ravel())

    # Build classification model for BUY/HOLD/SELL labels.
    decision_model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )

    # Fit classifier on same features but categorical action target.
    decision_model.fit(X_train, y_decision_train)

    # Predict on unseen test window.
    pred_next_close = price_model.predict(X_test)
    pred_decision = decision_model.predict(X_test)

    # Ground truth future prices from dataset.
    actual_next_close = next_close_test.to_numpy()

    # Naive baseline assumes no movement: tomorrow equals today's close.
    baseline_next_close = current_close_test.to_numpy()

    # Baseline error (lower is better).
    baseline_mae = float(mean_absolute_error(actual_next_close, baseline_next_close))

    # Model error (lower is better).
    model_mae = float(mean_absolute_error(actual_next_close, pred_next_close))

    # quality_ratio compares baseline to model.
    # >1.0 => model better than baseline, <1.0 => model worse than baseline.
    # Small epsilon prevents division by zero if model_mae is extremely tiny.
    quality_ratio = float(baseline_mae / max(model_mae, 1e-12))

    # Safety switch: if model quality is too low, activate baseline-protective mode.
    use_baseline = quality_ratio < BASELINE_HARD_CUTOFF

    # Choose blend weight according to model quality.
    # Low weight => conservative (closer to baseline), high weight => trust model more.
    if use_baseline:
        blend_weight = BASELINE_BLEND_WEIGHT
    elif quality_ratio < 1.0:
        blend_weight = BLEND_WEIGHT_WHEN_WEAKER
    else:
        blend_weight = BLEND_WEIGHT_WHEN_STRONGER

    # Store metrics for monitoring, confidence logic, and debugging in production.
    metrics = {
        # Average absolute price error.
        "mae": model_mae,

        # RMSE penalizes large misses more than MAE.
        "rmse": float(np.sqrt(mean_squared_error(actual_next_close, pred_next_close))),

        # R² indicates explained variance quality.
        "r2": float(r2_score(actual_next_close, pred_next_close)),

        # Baseline MAE to compare whether model adds value.
        "baseline_mae": baseline_mae,

        # Direct model-vs-baseline score used by trust/blending logic.
        "quality_ratio": quality_ratio,

        # Classifier accuracy on BUY/HOLD/SELL labels in test window.
        "decision_accuracy": float(accuracy_score(y_decision_test, pred_decision)),

        # Persist label thresholds so inference can use consistent decision boundaries.
        "decision_quantiles": {
            "lower": lower_q,
            "upper": upper_q,
        },

        # Explicit target type for forward compatibility in prediction logic.
        "target": "next_close_price",

        # Data volume metadata for observability and diagnostics.
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }

    # Artifact = full packaged model object saved to disk and later reloaded for inference.
    # It contains models, schema, metrics, training metadata, and trust controls.
    artifact = {
        # Regressor for numeric next-close prediction.
        "price_model": price_model,

        # Classifier for BUY/HOLD/SELL recommendation.
        "decision_model": decision_model,

        # Feature schema used during training (must match during prediction).
        "feature_columns": FEATURE_COLUMNS,

        # UTC timestamp for auditability and model freshness checks.
        "trained_at": datetime.now(timezone.utc).isoformat(),

        # Saved evaluation metrics.
        "metrics": metrics,

        # Identity metadata.
        "ticker": ticker.upper(),
        "period": str(period),

        # Forecast horizon metadata.
        "target_horizon_days": TARGET_HORIZON_DAYS,

        # Safety/trust controls used later in prediction blending.
        "use_baseline": use_baseline,
        "blend_weight": blend_weight,
    }

    # Build file path scoped to ticker+period so artifacts do not overwrite each other.
    model_path = model_path_for_ticker(ticker, period=period)

    # Ensure parent folder exists before writing artifact.
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Save artifact to disk; prediction service later reloads this file.
    joblib.dump(artifact, model_path)

    # Return artifact immediately so caller can use metrics/metadata without reloading from disk.
    return artifact