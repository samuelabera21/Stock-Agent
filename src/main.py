try:
    from .config import model_path_for_ticker
    from .fetch import fetch_stock_data
    from .features import add_features
    from .train import train_model
    from .predict import predict_price
except ImportError:
    from config import model_path_for_ticker
    from fetch import fetch_stock_data
    from features import add_features
    from train import train_model
    from predict import predict_price


def run(ticker="AAPL", period="5y", force_retrain=False):
    print("Fetching stock data...")

    ticker = (ticker or "AAPL").upper().strip()
    model_path = model_path_for_ticker(ticker)

    data = fetch_stock_data(ticker=ticker, period=period)
    data = add_features(data)

    trained = False
    artifact = None

    if force_retrain or not model_path.exists():
        artifact = train_model(data, ticker=ticker)
        trained = True

    try:
        prediction_info, loaded_artifact = predict_price(data, ticker=ticker)
    except ValueError as error:
        if "artifact format is invalid" not in str(error).lower() and "price model not found" not in str(error).lower():
            raise

        artifact = train_model(data, ticker=ticker)
        trained = True
        prediction_info, loaded_artifact = predict_price(data, ticker=ticker)

    if artifact is None:
        artifact = loaded_artifact

    close = data["Close"]
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]

    index_start = data.index.min()
    index_end = data.index.max()
    data_start = index_start.strftime("%Y-%m-%d") if hasattr(index_start, "strftime") else str(index_start)
    data_end = index_end.strftime("%Y-%m-%d") if hasattr(index_end, "strftime") else str(index_end)

    recent_volatility = float(data["Volatility"].iloc[-1])

    current = float(prediction_info["current_price"])
    predicted = float(prediction_info["final_price"])
    decision = prediction_info.get("model_decision", "HOLD")

    result = {
        "ticker": ticker,
        "current_price": current,
        "predicted_price": predicted,
        "model_price": float(prediction_info["model_price"]),
        "predicted_return": float(prediction_info["predicted_return"]),
        "decision": decision,
        "used_baseline": bool(prediction_info["used_baseline"]),
        "blend_weight": float(prediction_info.get("blend_weight", 1.0)),
        "confidence": prediction_info.get("confidence", "low"),
        "recent_volatility": recent_volatility,
        "model_trained": trained,
        "trained_at": artifact.get("trained_at") if artifact else None,
        "target_horizon_days": artifact.get("target_horizon_days") if artifact else 1,
        "metrics": artifact.get("metrics") if artifact else None,
        "recent_close_prices": [float(value) for value in close.tail(30).tolist()],
        "data_source": "Yahoo Finance (yfinance)",
        "data_period": period,
        "data_rows": int(len(data)),
        "data_start": data_start,
        "data_end": data_end,
        "model_file": str(model_path),
    }

    print(f"Current Price: {current:.2f}")
    print(f"Predicted Price: {predicted:.2f}")
    print(f"Decision: {decision}")

    return result


if __name__ == "__main__":
    run(force_retrain=True)