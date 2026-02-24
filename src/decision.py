def make_decision(current, predicted, recent_volatility=None):
    if current <= 0:
        return "HOLD"

    move_pct = (predicted - current) / current

    if move_pct > 0:
        return "BUY"
    if move_pct < 0:
        return "SELL"
    return "HOLD"