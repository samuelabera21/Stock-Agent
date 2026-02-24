import yfinance as yf


TICKER_FALLBACKS = {
    "GOOGL": "GOOG",
}


def fetch_stock_data(ticker="AAPL", period="5y", retries=3):
    data = None
    last_error = None
    ticker_candidates = [ticker]

    fallback = TICKER_FALLBACKS.get((ticker or "").upper())
    if fallback and fallback not in ticker_candidates:
        ticker_candidates.append(fallback)

    for current_ticker in ticker_candidates:
        for _ in range(retries):
            try:
                data = yf.download(current_ticker, period=period, progress=False, auto_adjust=False)
                if data is not None and not data.empty:
                    break
            except Exception as error:
                last_error = error

        if data is not None and not data.empty:
            break

    if data is None or data.empty:
        if last_error is not None:
            raise RuntimeError(f"Failed to fetch stock data for {ticker}: {last_error}")
        raise ValueError(f"No data returned for ticker '{ticker}'.")

    close = data.get("Close")
    if close is None:
        raise ValueError("Downloaded data does not contain a 'Close' column.")

    if getattr(close, "ndim", 1) == 2:
        data["Close"] = close.iloc[:, 0]

    data.dropna(inplace=True)

    if data.empty:
        raise ValueError(f"No valid rows left after cleaning data for ticker '{ticker}'.")

    return data