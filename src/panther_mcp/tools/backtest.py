from panther_mcp.client import PantherClient
from panther_mcp.models import Strategy


def run_backtest(
    client: PantherClient,
    symbol: str,
    timeframe: str,
    start_date: str,
    strategy: dict,
    end_date: str | None = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
) -> dict:
    """Define and execute a trading strategy backtest.

    The strategy is defined using entry/exit rules with indicators and conditions.
    The backtest runs asynchronously — use get_backtest_status to poll for completion.

    Args:
        symbol: Asset symbol, e.g. "BTC/USDT", "EUR/USD"
        timeframe: Candle timeframe — "1m", "5m", "15m", "1h", "4h", "1d", "1w"
        start_date: Backtest start date in ISO format
        strategy: Strategy definition with entry_rules, exit_rules, stop_loss, take_profit
        end_date: Backtest end date (defaults to today)
        initial_cash: Starting capital (default 10000)
        commission: Per-trade commission rate (default 0.001 = 0.1%)
    """
    # Validate strategy shape
    parsed = Strategy(**strategy)

    payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": start_date,
        "strategy": parsed.model_dump(),
        "initial_cash": initial_cash,
        "commission": commission,
    }
    if end_date:
        payload["end_date"] = end_date
    return client.post("/backtests/", json=payload)


def get_backtest_status(client: PantherClient, backtest_id: str) -> dict:
    """Check the status of a running backtest.

    Args:
        backtest_id: The ID returned by run_backtest
    """
    return client.get(f"/backtests/{backtest_id}/status/")
