import joblib  # joblib loads the trained artifact file (saved models + metadata) from disk.

try:
    # Package-style import path (works when running inside module/package context).
    from .config import BASELINE_BLEND_WEIGHT, FEATURE_COLUMNS, model_path_for_ticker
except ImportError:
    # Script-style fallback import (works when running this file directly).
    from config import BASELINE_BLEND_WEIGHT, FEATURE_COLUMNS, model_path_for_ticker


def load_artifact(ticker="AAPL", period="5y"):
    # Build the expected model file path for this ticker and data period.
    # Example outcome: models/model_AAPL_5y.pkl
    model_path = model_path_for_ticker(ticker, period=period)

    # Safety check: do not continue if trained model file does not exist.
    if not model_path.exists():
        raise FileNotFoundError("Model artifact not found. Train the model first.")

    # Deserialize (load) artifact from disk into Python object.
    artifact = joblib.load(model_path)

    # Validate loaded object type to avoid runtime surprises.
    if not isinstance(artifact, dict):
        raise ValueError("Model artifact format is invalid.")

    # Ensure required regression model exists in the artifact.
    if "price_model" not in artifact:
        raise ValueError("Model artifact format is invalid.")

    # Verify artifact period matches request, preventing wrong-model usage.
    artifact_period = str(artifact.get("period", period))
    if artifact_period != str(period):
        raise ValueError(
            f"Model period mismatch (artifact: {artifact_period}, requested: {period}). Retrain for requested period."
        )

    # Return validated artifact for prediction.
    return artifact


def predict_price(data, ticker="AAPL", period="5y"):
    # Load trained models + metadata for requested ticker/period.
    artifact = load_artifact(ticker=ticker, period=period)

    # Regressor: predicts numeric next price.
    price_model = artifact.get("price_model")

    # Classifier: optional second opinion for BUY/HOLD/SELL.
    decision_model = artifact.get("decision_model")

    # Regressor is mandatory; without it we cannot compute numeric forecast.
    if price_model is None:
        raise ValueError("Price model not found in artifact.")

    # Prefer feature schema saved in artifact to guarantee train/predict consistency.
    # Fallback to current config list if artifact does not store it.
    feature_columns = artifact.get("feature_columns", FEATURE_COLUMNS)

    # Check incoming dataframe has all required feature columns.
    missing = [column for column in feature_columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required feature columns for prediction: {missing}")

    # Read close series from incoming data.
    close = data["Close"]

    # Normalize close to 1D if provider returned a 2D column structure.
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]

    # Current market price = latest available close.
    current_price = float(close.iloc[-1])

    # Build one-row feature input using latest row only (predict next step from current state).
    latest = data[feature_columns].iloc[-1:]

    # Raw regression output from model.
    raw_prediction = float(price_model.predict(latest)[0])

    # Identify what the regressor output means.
    # If target is next_close_price -> raw output is already a price.
    # Else assume output is return and convert to price.
    target_type = artifact.get("metrics", {}).get("target")
    if target_type == "next_close_price":
        model_price = raw_prediction
    else:
        model_price = current_price * (1.0 + raw_prediction)

    # Convert model price into model-implied return.
    model_predicted_return = (model_price / current_price) - 1.0

    # Read safety settings learned/selected at training time.
    use_baseline = bool(artifact.get("use_baseline", False))
    artifact_blend_weight = float(artifact.get("blend_weight", 1.0))

    # Clamp blend weight into valid range [0, 1].
    if artifact_blend_weight < 0.0:
        artifact_blend_weight = 0.0
    if artifact_blend_weight > 1.0:
        artifact_blend_weight = 1.0

    # If baseline mode is enabled but weight is zero, apply safe default baseline blend.
    if use_baseline and artifact_blend_weight == 0.0:
        artifact_blend_weight = float(BASELINE_BLEND_WEIGHT)

    # Applied weight determines how much final price trusts model vs current price baseline.
    applied_blend_weight = 0.0 if use_baseline else artifact_blend_weight

    # In baseline mode we still honor artifact blend setting (explicit control).
    if use_baseline:
        applied_blend_weight = artifact_blend_weight

    # Blend model prediction with current price for stability.
    final_price = (applied_blend_weight * model_price) + ((1.0 - applied_blend_weight) * current_price)

    # Final blended return reported to consumers.
    predicted_return = (final_price / current_price) - 1.0

    # Decision logic uses pure model-implied return (before blend), by design.
    decision_return = model_predicted_return

    # Retrieve metrics payload saved during training.
    metrics = artifact.get("metrics", {})

    # Read quantile thresholds used to map returns into SELL/HOLD/BUY.
    decision_quantiles = metrics.get("decision_quantiles", {}) if isinstance(metrics, dict) else {}
    lower_q = float(decision_quantiles.get("lower", -0.002))
    upper_q = float(decision_quantiles.get("upper", 0.002))

    # Safety fallback if thresholds are invalid.
    if lower_q >= upper_q:
        lower_q, upper_q = -0.002, 0.002

    # Quantile-based decision from regression return.
    if decision_return <= lower_q:
        quantile_decision = "SELL"
    elif decision_return >= upper_q:
        quantile_decision = "BUY"
    else:
        quantile_decision = "HOLD"

    # Optional classifier prediction (second opinion).
    classifier_decision = None
    if decision_model is not None:
        try:
            # Classifier predicts one of BUY/SELL/HOLD from latest features.
            classifier_decision = str(decision_model.predict(latest)[0])
        except Exception:
            # Do not fail whole prediction if classifier has an issue; continue with quantile decision.
            classifier_decision = None

    # Consensus policy:
    # If classifier and regression-quantile agree, mark joint source.
    # Otherwise trust regression-quantile as deterministic fallback.
    if classifier_decision in {"BUY", "SELL", "HOLD"} and classifier_decision == quantile_decision:
        final_decision = classifier_decision
        decision_source = "regression+classifier"
    else:
        final_decision = quantile_decision
        decision_source = "regression-quantile"

    # Confidence derived from training quality ratio (model error vs baseline error).
    quality_ratio = float(metrics.get("quality_ratio", 0.0))
    if quality_ratio >= 1.0:
        confidence = "high"
    elif quality_ratio >= 0.8:
        confidence = "medium"
    else:
        confidence = "low"

    # Final prediction payload returned to API/frontend.
    # Contains prices, returns, safety flags, decision details, and thresholds for transparency.
    prediction_info = {
        # Latest market close.
        "current_price": current_price,

        # Final blended expected return.
        "predicted_return": float(predicted_return),

        # Raw model-implied return before blending.
        "model_predicted_return": float(model_predicted_return),

        # Return value used for quantile decision logic.
        "decision_return": float(decision_return),

        # Price predicted directly by model (before blending).
        "model_price": float(model_price),

        # Final price after model/baseline blend.
        "final_price": float(final_price),

        # Whether baseline-protective mode is enabled.
        "used_baseline": bool(use_baseline),

        # Applied blend weight used to compute final_price.
        "blend_weight": applied_blend_weight,

        # Confidence label (high/medium/low) from quality ratio.
        "confidence": confidence,

        # Final BUY/HOLD/SELL decision consumed by UI/API.
        "model_decision": final_decision,

        # Optional classifier output (can be None).
        "classifier_decision": classifier_decision,

        # Indicates whether final decision came from consensus or regression fallback.
        "decision_source": decision_source,

        # Persist explicit decision boundaries used in this prediction.
        "decision_thresholds": {
            "sell_below_or_equal": lower_q,
            "buy_above_or_equal": upper_q,
        },
    }

    # Return both result payload and full artifact for callers that need metadata/models.
    return prediction_info, artifact