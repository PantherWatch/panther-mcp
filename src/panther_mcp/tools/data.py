from panther_mcp.client import PantherClient


def list_available_assets(
    client: PantherClient,
    asset_type: str | None = None,
    search: str | None = None,
) -> dict:
    """List tradeable assets available for backtesting.

    Args:
        asset_type: Filter by type — "crypto", "forex", or "commodity"
        search: Search by symbol or name, e.g. "BTC" or "EUR/USD"
    """
    params = {}
    if asset_type:
        params["asset_type"] = asset_type
    if search:
        params["search"] = search
    assets = client.get("/assets/", params=params)
    return {"assets": assets, "total": len(assets)}


def get_price_data(
    client: PantherClient,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str | None = None,
) -> dict:
    """Fetch historical OHLCV price data for a given asset.

    Returns summary stats and a preview (first/last rows), not the full dataset.

    Args:
        symbol: Asset symbol, e.g. "BTC/USDT", "EUR/USD", "XAUUSD"
        timeframe: Candle timeframe — "1m", "5m", "15m", "1h", "4h", "1d", "1w"
        start_date: Start date in ISO format, e.g. "2024-01-01"
        end_date: End date in ISO format (defaults to today)
    """
    params = {
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": start_date,
    }
    if end_date:
        params["end_date"] = end_date
    return client.get("/data/", params=params)
