def add_features(data):
    if "Close" not in data.columns:
        raise ValueError("Input data is missing required column: Close")

    close = data["Close"]
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]
    data["Close"] = close

    data["MA10"] = close.rolling(10).mean()
    data["MA20"] = close.rolling(20).mean()
    data["MA50"] = close.rolling(50).mean()

    data["EMA12"] = close.ewm(span=12, adjust=False).mean()
    data["EMA26"] = close.ewm(span=26, adjust=False).mean()
    data["MACD"] = data["EMA12"] - data["EMA26"]

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    data["RSI14"] = 100 - (100 / (1 + rs))

    data["Return1"] = close.pct_change(1)
    data["Return5"] = close.pct_change(5)
    data["Volatility"] = data["Return1"].rolling(10).std()

    if "Volume" in data.columns:
        volume = data["Volume"]
        if getattr(volume, "ndim", 1) == 2:
            volume = volume.iloc[:, 0]
        data["VolumeChange"] = volume.pct_change().replace([float("inf"), float("-inf")], 0)
    else:
        data["VolumeChange"] = 0.0

    data.dropna(inplace=True)

    if data.empty:
        raise ValueError("Feature engineering produced no rows. Try using a longer data period.")

    return data