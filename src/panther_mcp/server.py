from fastmcp import FastMCP

from .client import PantherClient
from .tools.backtest import get_backtest_status, run_backtest
from .tools.data import get_price_data, list_available_assets
from .tools.results import get_backtest_results, list_backtests

mcp = FastMCP(
    "Panther",
    instructions=(
        "Panther lets you backtest trading strategies. "
        "Start by listing available assets, then examine price data, "
        "define a strategy with entry/exit rules using indicators, "
        "run a backtest, and review the results. "
        "You can iterate on strategies to find the best one."
    ),
)

_client: PantherClient | None = None


def _get_client() -> PantherClient:
    global _client
    if _client is None:
        _client = PantherClient()
    return _client


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
    - entry_rules: List of rules that trigger a buy signal
    - exit_rules: List of rules that trigger a sell signal
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


# --- Results tools ---


@mcp.tool()
def tool_get_backtest_results(backtest_id: str) -> dict:
    """Get the results of a completed backtest.

    Returns:
    - summary: Key metrics (total return, Sharpe ratio, max drawdown, win rate, etc.)
    - trades_preview: First 10 trades with entry/exit dates and P&L
    - full_results_url: Link to full results data
    - results_url: Shareable link to view results on panther.watch
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


# --- Resources (documentation for Claude) ---

STRATEGIES_DOC = """# Panther Strategy Guide

## Supported Indicators

### SMA (Simple Moving Average)
- params: {"period": int}
- Example: {"indicator": "SMA", "params": {"period": 50}}

### EMA (Exponential Moving Average)
- params: {"period": int}
- Example: {"indicator": "EMA", "params": {"period": 20}}

### RSI (Relative Strength Index)
- params: {"period": int} (default 14)
- Returns values 0-100. Overbought > 70, oversold < 30.
- Example: {"indicator": "RSI", "params": {"period": 14}}

### MACD (Moving Average Convergence Divergence)
- params: {"fast": int, "slow": int, "signal": int}
- Example: {"indicator": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}}

### BB (Bollinger Bands)
- params: {"period": int, "std": float}
- Returns upper, middle, lower bands.
- Example: {"indicator": "BB", "params": {"period": 20, "std": 2.0}}

## Conditions

- `crosses_above`: Indicator crosses above the comparison value
- `crosses_below`: Indicator crosses below the comparison value
- `greater_than`: Indicator is above the comparison value
- `less_than`: Indicator is below the comparison value
- `equals`: Indicator equals the comparison value

## compare_to

Can be either:
- Another indicator: {"indicator": "SMA", "params": {"period": 200}}
- A numeric value: 70 (e.g., RSI > 70)

## Example Strategies

### Golden Cross (SMA 50/200)
```json
{
  "name": "Golden Cross",
  "entry_rules": [
    {"indicator": "SMA", "params": {"period": 50}, "condition": "crosses_above",
     "compare_to": {"indicator": "SMA", "params": {"period": 200}}}
  ],
  "exit_rules": [
    {"indicator": "SMA", "params": {"period": 50}, "condition": "crosses_below",
     "compare_to": {"indicator": "SMA", "params": {"period": 200}}}
  ],
  "stop_loss": 0.05
}
```

### RSI Mean Reversion
```json
{
  "name": "RSI Mean Reversion",
  "entry_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_above", "compare_to": 30}
  ],
  "exit_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_above", "compare_to": 70}
  ],
  "stop_loss": 0.03,
  "take_profit": 0.10
}
```
"""

GETTING_STARTED_DOC = """# Getting Started with Panther

## Workflow

1. **List assets** — Use `list_available_assets` to find what you can backtest
2. **Examine data** — Use `get_price_data` to look at historical prices
3. **Define strategy** — Build a strategy with indicators and entry/exit rules
4. **Run backtest** — Use `run_backtest` to execute your strategy
5. **Check status** — Use `get_backtest_status` to poll until completed
6. **Review results** — Use `get_backtest_results` for metrics and a link to full results
7. **Iterate** — Adjust parameters, try different indicators, compare results

## Tips

- Start with simple strategies (single indicator) before adding complexity
- Compare strategies across different timeframes and date ranges
- Use stop_loss and take_profit to manage risk
- Check the full results on panther.watch for equity curves and trade details
"""


@mcp.resource("panther://docs/strategies")
def strategies_doc() -> str:
    """Documentation on supported indicators, conditions, and example strategies."""
    return STRATEGIES_DOC


@mcp.resource("panther://docs/getting-started")
def getting_started_doc() -> str:
    """Quick start guide for backtesting with Panther."""
    return GETTING_STARTED_DOC
