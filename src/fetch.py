# Import the yfinance library.
# This library allows Python to download stock data from Yahoo Finance.
import yfinance as yf


# This dictionary is used if a ticker symbol needs an alternative name.
# Example: Sometimes Yahoo uses GOOG instead of GOOGL.
TICKER_FALLBACKS = {
    "GOOGL": "GOOG",
}


# This function downloads stock data.
# ticker  → stock symbol (default: AAPL)
# period  → how much historical data (default: 5 years)
# retries → how many times to try if download fails
def fetch_stock_data(ticker="AAPL", period="5y", retries=3):

    # Will store the downloaded stock data (as a table/DataFrame)
    data = None

    # Will store any error that happens during download
    last_error = None

    # Start with a list containing the original ticker
    ticker_candidates = [ticker]


    # Convert ticker to uppercase and check if a fallback exists
    fallback = TICKER_FALLBACKS.get((ticker or "").upper())

    # If fallback exists and is not already in the list, add it
    if fallback and fallback not in ticker_candidates:
        ticker_candidates.append(fallback)


    # Try each possible ticker (original + fallback if exists)
    for current_ticker in ticker_candidates:

        # Try downloading multiple times if needed
        for _ in range(retries):
            try:
                # Download stock data from Yahoo Finance
                # period="5y" means last 5 years
                # progress=False hides progress bar
                # auto_adjust=False keeps raw prices (no dividend adjustment)
                data = yf.download(
                    current_ticker,
                    period=period,
                    progress=False,
                    auto_adjust=False
                )

                # If we successfully received non-empty data, stop retrying
                if data is not None and not data.empty:
                    break

            # If something goes wrong (internet issue, invalid ticker, etc.)
            except Exception as error:
                # Save the error so we can show it later
                last_error = error

        # If we successfully downloaded data, stop trying other tickers
        if data is not None and not data.empty:
            break


    # After trying everything, if still no data:
    if data is None or data.empty:

        # If there was an actual error (like network failure)
        if last_error is not None:
            raise RuntimeError(
                f"Failed to fetch stock data for {ticker}: {last_error}"
            )

        # If no error but Yahoo returned nothing
        raise ValueError(
            f"No data returned for ticker '{ticker}'."
        )


    # Get the "Close" price column from the downloaded data
    close = data.get("Close")

    # If Close column does not exist, stop (model needs it)
    if close is None:
        raise ValueError(
            "Downloaded data does not contain a 'Close' column."
        )


    # Sometimes Yahoo returns columns in a strange multi-level format.
    # If Close column has 2 dimensions, extract the first column only.
    if getattr(close, "ndim", 1) == 2:
        data["Close"] = close.iloc[:, 0]


    # Remove rows that contain missing (NaN) values
    data.dropna(inplace=True)


    # If removing missing values makes the dataset empty, stop
    if data.empty:
        raise ValueError(
            f"No valid rows left after cleaning data for ticker '{ticker}'."
        )


    # Return the cleaned stock data table
    return data