def add_features(data):
	# Ensure mandatory market price column exists; all other indicators depend on Close.
    if "Close" not in data.columns:
        raise ValueError("Input data is missing required column: Close")

	# Extract close prices as the primary signal used by most technical indicators.
    close = data["Close"]
	# Some data providers can return a 2D pandas dataframe column shape; normalize to a 1D series.
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]
	# Write normalized close back to the dataframe for consistent downstream use.
    data["Close"] = close

	# Simple moving averages (trend smoothing over different horizons).
    data["MA10"] = close.rolling(10).mean()
    data["MA20"] = close.rolling(20).mean()
    data["MA50"] = close.rolling(50).mean()

	# Exponential moving averages give more weight to recent prices.
    data["EMA12"] = close.ewm(span=12, adjust=False).mean()
    data["EMA26"] = close.ewm(span=26, adjust=False).mean()
	# MACD measures momentum shift using fast and slow EMA difference.
    data["MACD"] = data["EMA12"] - data["EMA26"]

	# Delta = day-to-day price change, then split into gains and losses for RSI computation.
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
	# Rolling average gains/losses over 14 periods (classic RSI window).
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
	# Relative strength ratio; protect division from zero with tiny epsilon.
    rs = avg_gain / avg_loss.replace(0, 1e-9)
	# RSI scale transformed to 0..100 where extremes can indicate overbought/oversold.
    data["RSI14"] = 100 - (100 / (1 + rs))

	# Percentage returns over 1 and 5 periods (short and medium movement signals).
    data["Return1"] = close.pct_change(1)
    data["Return5"] = close.pct_change(5)
	# Rolling standard deviation of 1-period returns as a volatility proxy.
    data["Volatility"] = data["Return1"].rolling(10).std()

	# Use real volume dynamics when volume exists, otherwise provide a neutral fallback.
    if "Volume" in data.columns:
        volume = data["Volume"]
		# Normalize volume shape similarly to Close (defensive handling for 2D output).
        if getattr(volume, "ndim", 1) == 2:
            volume = volume.iloc[:, 0]
		# Convert volume to rate-of-change and replace infinities from divide-by-zero cases.
        data["VolumeChange"] = volume.pct_change().replace([float("inf"), float("-inf")], 0)
    else:
		# If no volume is available, keep feature present with neutral constant.
        data["VolumeChange"] = 0.0

	# Remove rows with NaN introduced by rolling windows/pct_change warm-up periods.
    data.dropna(inplace=True)

	# Fail fast if the selected period is too short to produce valid engineered features.
    if data.empty:
        raise ValueError("Feature engineering produced no rows. Try using a longer data period.")

	# Return the enriched dataframe ready for model training/inference.
    return data