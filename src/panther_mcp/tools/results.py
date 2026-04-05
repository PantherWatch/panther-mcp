from panther_mcp.client import PantherClient


def get_backtest_results(client: PantherClient, backtest_id: str) -> dict:
    """Get the results of a completed backtest.

    Returns a summary with key metrics (return, Sharpe ratio, drawdown, etc.),
    a preview of trades, and a link to full interactive results on panther.watch.

    Args:
        backtest_id: The ID returned by run_backtest
    """
    return client.get(f"/backtests/{backtest_id}/results/")


def list_backtests(
    client: PantherClient,
    limit: int = 10,
    symbol: str | None = None,
) -> dict:
    """List your previous backtests with summary info.

    Args:
        limit: Maximum number of results (default 10)
        symbol: Filter by asset symbol
    """
    params = {"limit": limit}
    if symbol:
        params["symbol"] = symbol
    backtests = client.get("/backtests/", params=params)
    return {"backtests": backtests, "total": len(backtests)}
