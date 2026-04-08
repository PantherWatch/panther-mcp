from panther_mcp.client import PantherClient
from panther_mcp.models import Constraint, ParamRange, PortfolioAsset, Strategy


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
        "strategy": parsed.model_dump(exclude_none=True),
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


def optimize_strategy(
    client: PantherClient,
    symbol: str,
    timeframe: str,
    start_date: str,
    strategy: dict,
    param_ranges: list[dict],
    constraints: list[dict] | None = None,
    rank_by: str = "sharpe_ratio",
    end_date: str | None = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
) -> dict:
    """Submit a strategy optimization / parameter sweep."""
    parsed = Strategy(**strategy)
    validated_ranges = [ParamRange(**pr).model_dump() for pr in param_ranges]
    validated_constraints = (
        [Constraint(**c).model_dump() for c in constraints] if constraints else []
    )

    payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": start_date,
        "strategy": parsed.model_dump(exclude_none=True),
        "param_ranges": validated_ranges,
        "constraints": validated_constraints,
        "rank_by": rank_by,
        "initial_cash": initial_cash,
        "commission": commission,
    }
    if end_date:
        payload["end_date"] = end_date
    return client.post("/optimizations/", json=payload)


def get_optimization_status(client: PantherClient, optimization_id: str) -> dict:
    return client.get(f"/optimizations/{optimization_id}/status/")


def get_optimization_results(client: PantherClient, optimization_id: str) -> dict:
    return client.get(f"/optimizations/{optimization_id}/results/")


def run_portfolio_backtest(
    client: PantherClient,
    assets: list[dict],
    timeframe: str,
    start_date: str,
    strategy: dict,
    end_date: str | None = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
) -> dict:
    """Submit a portfolio backtest across multiple assets.

    Args:
        assets: List of {"symbol": "BTC/USDT", "weight": 0.6} dicts. Weights must sum to 1.0.
        timeframe: Candle timeframe
        start_date: Start date in ISO format
        strategy: Strategy definition (applied to all assets)
        end_date: End date (defaults to today)
        initial_cash: Total starting capital (default 10000)
        commission: Per-trade commission rate (default 0.001)
    """
    parsed_strategy = Strategy(**strategy)
    validated_assets = [PortfolioAsset(**a).model_dump() for a in assets]

    payload = {
        "assets": validated_assets,
        "timeframe": timeframe,
        "start_date": start_date,
        "strategy": parsed_strategy.model_dump(exclude_none=True),
        "initial_cash": initial_cash,
        "commission": commission,
    }
    if end_date:
        payload["end_date"] = end_date
    return client.post("/portfolios/", json=payload)


def get_portfolio_backtest_status(
    client: PantherClient, portfolio_backtest_id: str
) -> dict:
    return client.get(f"/portfolios/{portfolio_backtest_id}/status/")


def get_portfolio_backtest_results(
    client: PantherClient, portfolio_backtest_id: str
) -> dict:
    return client.get(f"/portfolios/{portfolio_backtest_id}/results/")
