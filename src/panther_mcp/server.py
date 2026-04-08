from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from .auth import PantherTokenVerifier
from .client import PantherClient
from .tools.backtest import (
    get_backtest_status,
    get_optimization_results,
    get_optimization_status,
    get_portfolio_backtest_results,
    get_portfolio_backtest_status,
    optimize_strategy,
    run_backtest,
    run_portfolio_backtest,
)
from .tools.data import get_price_data, list_available_assets
from .tools.results import get_backtest_results, list_backtests, list_optimizations

mcp = FastMCP(
    "Panther",
    auth=PantherTokenVerifier(),
    instructions=(
        "Panther lets you backtest trading strategies. "
        "Start by listing available assets, then examine price data, "
        "define a strategy with entry/exit rules using indicators, "
        "run a backtest, and review the results. "
        "You can iterate on strategies to find the best one."
    ),
)

_stdio_client: PantherClient | None = None


def _get_client() -> PantherClient:
    """Get a PantherClient for the current request.

    Hosted (Streamable HTTP): uses the Bearer token from the request.
    Local (stdio): uses PANTHER_API_KEY env var, cached for the session.
    """
    token = get_access_token()
    if token:
        return PantherClient(api_key=token.token)
    global _stdio_client
    if _stdio_client is None:
        _stdio_client = PantherClient()
    return _stdio_client


# --- Data tools ---


@mcp.tool()
def tool_list_available_assets(
    asset_type: str | None = None,
    search: str | None = None,
) -> dict:
    """List tradeable assets available for backtesting.

    Filter by asset type (crypto, forex, commodity) and/or search by symbol or name.
    """
    return list_available_assets(_get_client(), asset_type=asset_type, search=search)


@mcp.tool()
def tool_get_price_data(
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str | None = None,
) -> dict:
    """Fetch historical OHLCV price data for an asset.

    Returns summary statistics and a preview of the data (not the full dataset).
    Use this to examine price history before defining a backtest strategy.

    Timeframes: 1m, 5m, 15m, 1h, 4h, 1d, 1w
    """
    return get_price_data(_get_client(), symbol, timeframe, start_date, end_date)


# --- Backtest tools ---


@mcp.tool()
def tool_run_backtest(
    symbol: str,
    timeframe: str,
    start_date: str,
    strategy: dict,
    end_date: str | None = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
) -> dict:
    """Define and execute a trading strategy backtest.

    The strategy object must include:
    - name: Strategy name
    - direction (optional): "long" (default), "short", or "both"
      - "long": entry_rules trigger buys, exit_rules trigger sells
      - "short": entry_rules trigger short entries, exit_rules trigger short covers
      - "both": uses entry_rules/exit_rules for longs, plus short_entry_rules/short_exit_rules for shorts
    - entry_rules: List of rules that trigger entry
    - exit_rules: List of rules that trigger exit
    - short_entry_rules (required when direction="both"): Rules for short entries
    - short_exit_rules (required when direction="both"): Rules for short exits
    - stop_loss (optional): Stop loss as fraction (0.05 = 5%)
    - take_profit (optional): Take profit as fraction (0.15 = 15%)

    Each rule has:
    - indicator: SMA, EMA, RSI, MACD, or BB
    - params: Indicator parameters (e.g. {"period": 50})
    - condition: crosses_above, crosses_below, greater_than, less_than, equals
    - compare_to: Another indicator object or a numeric value

    Returns a backtest_id. Use get_backtest_status to poll for completion,
    then get_backtest_results for the full results.
    """
    return run_backtest(
        _get_client(),
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        strategy=strategy,
        end_date=end_date,
        initial_cash=initial_cash,
        commission=commission,
    )


@mcp.tool()
def tool_get_backtest_status(backtest_id: str) -> dict:
    """Check the status of a running backtest.

    Returns status (queued, running, completed, failed) and progress percentage.
    """
    return get_backtest_status(_get_client(), backtest_id)


# --- Optimization tools ---


@mcp.tool()
def tool_optimize_strategy(
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
    """Run a strategy optimization / parameter sweep.

    Tests multiple parameter combinations and ranks results by a metric.

    param_ranges: List of parameter ranges to sweep. Each has:
    - rule_path: Path to the parameter, e.g. "entry_rules[0].params.period"
    - start: Start value (inclusive)
    - end: End value (inclusive)
    - step: Step size

    constraints: Optional list of cross-parameter constraints, e.g.
    [{"left": "entry_rules[0].params.period", "op": "<", "right": "exit_rules[0].params.period"}]

    rank_by: Metric to rank results by (default "sharpe_ratio").
    Options: total_return, sharpe_ratio, max_drawdown, win_rate, profit_factor, total_trades

    Returns an optimization_id. Use get_optimization_status to poll,
    then get_optimization_results for ranked results.
    """
    return optimize_strategy(
        _get_client(),
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        strategy=strategy,
        param_ranges=param_ranges,
        constraints=constraints,
        rank_by=rank_by,
        end_date=end_date,
        initial_cash=initial_cash,
        commission=commission,
    )


@mcp.tool()
def tool_get_optimization_status(optimization_id: str) -> dict:
    """Check the status of a running optimization.

    Returns status, progress percentage, total and completed combinations.
    """
    return get_optimization_status(_get_client(), optimization_id)


@mcp.tool()
def tool_get_optimization_results(optimization_id: str) -> dict:
    """Get the results of a completed optimization.

    Returns:
    - best: The best parameter combination with its summary metrics
    - results: All combinations ranked by the chosen metric
    - total_combinations: How many combinations were tested
    - rank_by: The metric used for ranking
    """
    return get_optimization_results(_get_client(), optimization_id)


# --- Results tools ---


@mcp.tool()
def tool_get_backtest_results(backtest_id: str) -> dict:
    """Get the results of a completed backtest.

    Returns:
    - summary: Key metrics (total return, Sharpe ratio, max drawdown, win rate, etc.)
    - trades_preview: First 10 trades with entry/exit dates and P&L
    - full_results_url: Link to full results data
    - results_url: Shareable link to view results on panther.watch

    IMPORTANT: Always share the results_url link with the user so they can view
    the full results with equity curve and trade details on panther.watch.
    """
    return get_backtest_results(_get_client(), backtest_id)


@mcp.tool()
def tool_list_backtests(
    limit: int = 10,
    symbol: str | None = None,
) -> dict:
    """List your previous backtests with summary info.

    Use this to review past experiments and compare strategies.
    """
    return list_backtests(_get_client(), limit=limit, symbol=symbol)


@mcp.tool()
def tool_list_optimizations(
    limit: int = 10,
    symbol: str | None = None,
) -> dict:
    """List your previous optimizations / parameter sweeps.

    Use this to review past optimization runs and their best parameters.
    """
    return list_optimizations(_get_client(), limit=limit, symbol=symbol)


# --- Portfolio Backtest tools ---


@mcp.tool()
def tool_run_portfolio_backtest(
    assets: list[dict],
    timeframe: str,
    start_date: str,
    strategy: dict,
    end_date: str | None = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
) -> dict:
    """Run a portfolio backtest across multiple assets with weighted allocation.

    Test how a strategy performs across a diversified portfolio. Each asset gets
    a weighted allocation of the total capital.

    assets: List of asset allocations. Each has:
    - symbol: Asset symbol (e.g. "BTC/USDT", "ETH/USDT")
    - weight: Portfolio weight from 0 to 1. All weights must sum to 1.0.

    Example: [{"symbol": "BTC/USDT", "weight": 0.6}, {"symbol": "ETH/USDT", "weight": 0.4}]

    The same strategy is applied to all assets. Returns a portfolio_backtest_id.
    Use get_portfolio_backtest_status to poll, then get_portfolio_backtest_results for results.
    """
    return run_portfolio_backtest(
        _get_client(),
        assets=assets,
        timeframe=timeframe,
        start_date=start_date,
        strategy=strategy,
        end_date=end_date,
        initial_cash=initial_cash,
        commission=commission,
    )


@mcp.tool()
def tool_get_portfolio_backtest_status(portfolio_backtest_id: str) -> dict:
    """Check the status of a running portfolio backtest.

    Returns status (queued, running, completed, failed) and progress percentage.
    """
    return get_portfolio_backtest_status(_get_client(), portfolio_backtest_id)


@mcp.tool()
def tool_get_portfolio_backtest_results(portfolio_backtest_id: str) -> dict:
    """Get the results of a completed portfolio backtest.

    Returns:
    - summary: Portfolio-level metrics (total return, Sharpe ratio, max drawdown, total trades)
    - per_asset_results: Performance breakdown per asset
    - trades_preview: Recent trades across all assets
    - results_url: Shareable link to view results on panther.watch

    IMPORTANT: Always share the results_url link with the user so they can view
    the full results with equity curve, per-asset breakdown, and trade details on panther.watch.
    """
    return get_portfolio_backtest_results(_get_client(), portfolio_backtest_id)


# --- Resources (documentation for Claude) ---

_DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"


def _load_doc(filename: str) -> str:
    path = _DOCS_DIR / filename
    if path.exists():
        return path.read_text()
    return f"Documentation file {filename} not found."


STRATEGIES_DOC = _load_doc("STRATEGIES.md")
GETTING_STARTED_DOC = _load_doc("GETTING_STARTED.md")


@mcp.resource("panther://docs/strategies")
def strategies_doc() -> str:
    """Documentation on supported indicators, conditions, and example strategies."""
    return STRATEGIES_DOC


@mcp.resource("panther://docs/getting-started")
def getting_started_doc() -> str:
    """Quick start guide for backtesting with Panther."""
    return GETTING_STARTED_DOC
