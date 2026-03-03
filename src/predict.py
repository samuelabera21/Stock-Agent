import joblib

try:
    from .config import FEATURE_COLUMNS, model_path_for_ticker
except ImportError:
    from config import FEATURE_COLUMNS, model_path_for_ticker


def load_artifact(ticker="AAPL", period="5y"):
    model_path = model_path_for_ticker(ticker, period=period)

    if not model_path.exists():
        raise FileNotFoundError("Model artifact not found. Train the model first.")

    artifact = joblib.load(model_path)
    if not isinstance(artifact, dict):
        raise ValueError("Model artifact format is invalid.")

    if "price_model" not in artifact:
        raise ValueError("Model artifact format is invalid.")

    artifact_period = str(artifact.get("period", period))
    if artifact_period != str(period):
        raise ValueError(
            f"Model period mismatch (artifact: {artifact_period}, requested: {period}). Retrain for requested period."
        )

    return artifact


def predict_price(data, ticker="AAPL", period="5y"):
    artifact = load_artifact(ticker=ticker, period=period)
    price_model = artifact.get("price_model")
    decision_model = artifact.get("decision_model")

    if price_model is None:
        raise ValueError("Price model not found in artifact.")

    feature_columns = artifact.get("feature_columns", FEATURE_COLUMNS)

    missing = [column for column in feature_columns if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required feature columns for prediction: {missing}")

    close = data["Close"]
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]

    current_price = float(close.iloc[-1])
    latest = data[feature_columns].iloc[-1:]
    raw_prediction = float(price_model.predict(latest)[0])

    target_type = artifact.get("metrics", {}).get("target")
    if target_type == "next_close_price":
        model_price = raw_prediction
    else:
        model_price = current_price * (1.0 + raw_prediction)

    predicted_return = (model_price / current_price) - 1.0

    metrics = artifact.get("metrics", {})
    decision_quantiles = metrics.get("decision_quantiles", {}) if isinstance(metrics, dict) else {}
    lower_q = float(decision_quantiles.get("lower", -0.002))
    upper_q = float(decision_quantiles.get("upper", 0.002))

    if lower_q >= upper_q:
        lower_q, upper_q = -0.002, 0.002

    if predicted_return <= lower_q:
        quantile_decision = "SELL"
    elif predicted_return >= upper_q:
        quantile_decision = "BUY"
    else:
        quantile_decision = "HOLD"

    classifier_decision = None
    if decision_model is not None:
        try:
            classifier_decision = str(decision_model.predict(latest)[0])
        except Exception:
            classifier_decision = None

    if classifier_decision in {"BUY", "SELL", "HOLD"} and classifier_decision == quantile_decision:
        final_decision = classifier_decision
        decision_source = "regression+classifier"
    else:
        final_decision = quantile_decision
        decision_source = "regression-quantile"

    use_baseline = False
    applied_blend_weight = 1.0
    final_price = model_price

    quality_ratio = float(metrics.get("quality_ratio", 0.0))
    if quality_ratio >= 1.0:
        confidence = "high"
    elif quality_ratio >= 0.8:
        confidence = "medium"
    else:
        confidence = "low"

    prediction_info = {
        "current_price": current_price,
        "predicted_return": predicted_return,
        "model_price": float(model_price),
        "final_price": float(final_price),
        "used_baseline": use_baseline,
        "blend_weight": applied_blend_weight,
        "confidence": confidence,
        "model_decision": final_decision,
        "classifier_decision": classifier_decision,
        "decision_source": decision_source,
        "decision_thresholds": {
            "sell_below_or_equal": lower_q,
            "buy_above_or_equal": upper_q,
        },
    }

    return prediction_info, artifact