"""End-to-end tests for MCP tools against a running Django backend + Celery worker.

These are the MVP acceptance criteria. All flows that were validated manually
during development are encoded here.

Run with the full stack running (docker compose up):
    cd mcp
    PANTHER_API_KEY=pthr_<your_key> PANTHER_API_URL=http://localhost:8000/api/v1 \
        uv run pytest tests/test_e2e.py -v

Skipped by default in CI (no backend running).
"""

import os
import time

import pytest

from panther_mcp.client import PantherClient
from panther_mcp.tools.backtest import get_backtest_status, run_backtest
from panther_mcp.tools.data import get_price_data, list_available_assets
from panther_mcp.tools.results import get_backtest_results, list_backtests

BACKEND_URL = os.environ.get("PANTHER_API_URL", "")
HAS_BACKEND = bool(BACKEND_URL)

skip_no_backend = pytest.mark.skipif(
    not HAS_BACKEND,
    reason="PANTHER_API_URL not set — no live backend to test against",
)

BACKTEST_POLL_INTERVAL = 1  # seconds
BACKTEST_TIMEOUT = 120  # seconds


def _wait_for_backtest(client, backtest_id):
    """Poll until backtest completes or fails. Returns final status dict."""
    elapsed = 0
    while elapsed < BACKTEST_TIMEOUT:
        status = get_backtest_status(client, backtest_id)
        if status["status"] in ("completed", "failed"):
            return status
        time.sleep(BACKTEST_POLL_INTERVAL)
        elapsed += BACKTEST_POLL_INTERVAL
    pytest.fail(f"Backtest {backtest_id} timed out after {BACKTEST_TIMEOUT}s")


@pytest.fixture
def client():
    return PantherClient()


# ---------------------------------------------------------------------------
# Flow 1: Asset discovery
# ---------------------------------------------------------------------------


@skip_no_backend
class TestListAvailableAssetsE2E:
    def test_returns_assets(self, client):
        result = list_available_assets(client)
        assert "assets" in result
        assert result["total"] > 0

    def test_has_crypto_assets(self, client):
        result = list_available_assets(client, asset_type="crypto")
        symbols = [a["symbol"] for a in result["assets"]]
        assert "BTC/USDT" in symbols
        assert "ETH/USDT" in symbols

    def test_has_forex_assets(self, client):
        result = list_available_assets(client, asset_type="forex")
        symbols = [a["symbol"] for a in result["assets"]]
        assert "EUR/USD" in symbols

    def test_has_commodity_assets(self, client):
        result = list_available_assets(client, asset_type="commodity")
        symbols = [a["symbol"] for a in result["assets"]]
        assert "XAU/USD" in symbols

    def test_search_works(self, client):
        result = list_available_assets(client, search="btc")
        assert result["total"] >= 1
        assert all("BTC" in a["symbol"] for a in result["assets"])

    def test_asset_structure(self, client):
        result = list_available_assets(client, asset_type="crypto")
        asset = result["assets"][0]
        assert "symbol" in asset
        assert "name" in asset
        assert "asset_type" in asset
        assert "exchange" in asset
        assert "base_currency" in asset
        assert "quote_currency" in asset


# ---------------------------------------------------------------------------
# Flow 2: Price data inspection
# ---------------------------------------------------------------------------


@skip_no_backend
class TestGetPriceDataE2E:
    def test_fetch_btc_daily(self, client):
        result = get_price_data(
            client,
            symbol="BTC/USDT",
            timeframe="1d",
            start_date="2025-01-01",
            end_date="2025-03-31",
        )
        assert result["symbol"] == "BTC/USDT"
        assert result["total_candles"] > 0
        assert len(result["first_rows"]) > 0
        assert len(result["last_rows"]) > 0

    def test_summary_stats(self, client):
        result = get_price_data(
            client,
            symbol="ETH/USDT",
            timeframe="1d",
            start_date="2024-06-01",
            end_date="2024-06-30",
        )
        summary = result["summary"]
        assert summary["high"] > summary["low"]
        assert summary["avg_close"] > 0
        assert "price_change_pct" in summary

    def test_cached_request(self, client):
        params = dict(
            symbol="SOL/USDT",
            timeframe="1d",
            start_date="2024-03-01",
            end_date="2024-03-10",
        )
        r1 = get_price_data(client, **params)
        r2 = get_price_data(client, **params)
        assert r1["total_candles"] == r2["total_candles"]


# ---------------------------------------------------------------------------
# Flow 3: Golden cross backtest (SMA 50/200 on BTC/USDT)
# ---------------------------------------------------------------------------


@skip_no_backend
class TestGoldenCrossBacktestE2E:
    """The core MVP flow: describe strategy → backtest → get results."""

    STRATEGY = {
        "name": "Golden Cross SMA 50/200",
        "entry_rules": [
            {
                "indicator": "SMA",
                "params": {"period": 50},
                "condition": "crosses_above",
                "compare_to": {"indicator": "SMA", "params": {"period": 200}},
            }
        ],
        "exit_rules": [
            {
                "indicator": "SMA",
                "params": {"period": 50},
                "condition": "crosses_below",
                "compare_to": {"indicator": "SMA", "params": {"period": 200}},
            }
        ],
        "stop_loss": 0.05,
        "take_profit": 0.15,
    }

    def test_full_backtest_flow(self, client):
        # Step 1: Submit
        result = run_backtest(
            client,
            symbol="BTC/USDT",
            timeframe="1d",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy=self.STRATEGY,
            initial_cash=10000,
        )
        assert "backtest_id" in result
        assert result["status"] == "queued"
        backtest_id = result["backtest_id"]

        # Step 2: Wait for completion
        status = _wait_for_backtest(client, backtest_id)
        assert status["status"] == "completed"

        # Step 3: Get results
        results = get_backtest_results(client, backtest_id)
        summary = results["summary"]

        # Verify result structure
        assert "total_return" in summary
        assert "sharpe_ratio" in summary
        assert "max_drawdown" in summary
        assert "win_rate" in summary
        assert "total_trades" in summary
        assert isinstance(summary["total_trades"], int)
        assert summary["total_trades"] >= 0

        # Verify trades preview
        assert "trades_preview" in results
        assert isinstance(results["trades_preview"], list)

        # Verify shareable URL
        assert "results_url" in results
        assert f"/backtests/{backtest_id}" in results["results_url"]


# ---------------------------------------------------------------------------
# Flow 4: RSI strategy backtest
# ---------------------------------------------------------------------------


@skip_no_backend
class TestRSIBacktestE2E:
    STRATEGY = {
        "name": "RSI 14 Oversold/Overbought",
        "entry_rules": [
            {
                "indicator": "RSI",
                "params": {"period": 14},
                "condition": "less_than",
                "compare_to": 30,
            }
        ],
        "exit_rules": [
            {
                "indicator": "RSI",
                "params": {"period": 14},
                "condition": "greater_than",
                "compare_to": 70,
            }
        ],
        "stop_loss": None,
        "take_profit": None,
    }

    def test_rsi_backtest_completes(self, client):
        result = run_backtest(
            client,
            symbol="BTC/USDT",
            timeframe="1d",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy=self.STRATEGY,
        )
        backtest_id = result["backtest_id"]
        status = _wait_for_backtest(client, backtest_id)
        assert status["status"] == "completed"

        results = get_backtest_results(client, backtest_id)
        summary = results["summary"]
        # RSI strategy on BTC 2024 should produce some trades
        assert summary["total_trades"] > 0
        assert summary["win_rate"] >= 0
        assert summary["max_drawdown"] <= 0


# ---------------------------------------------------------------------------
# Flow 5: MACD crossover (multi-output indicator)
# ---------------------------------------------------------------------------


@skip_no_backend
class TestMACDCrossoverE2E:
    """Tests multi-output indicator handling: MACD line vs signal line."""

    STRATEGY = {
        "name": "MACD Crossover",
        "entry_rules": [
            {
                "indicator": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"},
                "condition": "crosses_above",
                "compare_to": {
                    "indicator": "MACD",
                    "params": {
                        "fast": 12,
                        "slow": 26,
                        "signal": 9,
                        "output": "signal_line",
                    },
                },
            }
        ],
        "exit_rules": [
            {
                "indicator": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"},
                "condition": "crosses_below",
                "compare_to": {
                    "indicator": "MACD",
                    "params": {
                        "fast": 12,
                        "slow": 26,
                        "signal": 9,
                        "output": "signal_line",
                    },
                },
            }
        ],
        "stop_loss": None,
        "take_profit": None,
    }

    def test_macd_crossover_completes(self, client):
        result = run_backtest(
            client,
            symbol="ETH/USDT",
            timeframe="1d",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy=self.STRATEGY,
        )
        backtest_id = result["backtest_id"]
        status = _wait_for_backtest(client, backtest_id)
        assert status["status"] == "completed"

        results = get_backtest_results(client, backtest_id)
        assert results["summary"]["total_trades"] > 0
        # Verify trade records have expected fields
        if results["trades_preview"]:
            trade = results["trades_preview"][0]
            assert "entry_date" in trade
            assert "exit_date" in trade
            assert "entry_price" in trade
            assert "exit_price" in trade
            assert "pnl" in trade
            assert "return_pct" in trade


# ---------------------------------------------------------------------------
# Flow 6: List backtests
# ---------------------------------------------------------------------------


@skip_no_backend
class TestListBacktestsE2E:
    def test_list_after_backtests(self, client):
        """After running backtests above, list should return them."""
        result = list_backtests(client)
        assert "backtests" in result
        assert result["total"] > 0

    def test_list_with_limit(self, client):
        result = list_backtests(client, limit=2)
        assert len(result["backtests"]) <= 2

    def test_list_with_symbol_filter(self, client):
        result = list_backtests(client, symbol="BTC/USDT")
        for bt in result["backtests"]:
            assert bt["symbol"] == "BTC/USDT"

    def test_backtest_entry_structure(self, client):
        result = list_backtests(client, limit=1)
        if result["backtests"]:
            bt = result["backtests"][0]
            assert "id" in bt
            assert "symbol" in bt
            assert "timeframe" in bt
            assert "status" in bt
            assert "created_at" in bt
            assert "strategy_name" in bt


# ---------------------------------------------------------------------------
# Flow 7: Error handling
# ---------------------------------------------------------------------------


@skip_no_backend
class TestErrorHandlingE2E:
    def test_invalid_strategy_rejected(self, client):
        """Backend should reject invalid strategy with HTTP 400."""
        import httpx

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            run_backtest(
                client,
                symbol="BTC/USDT",
                timeframe="1d",
                start_date="2024-01-01",
                strategy={
                    "name": "Bad",
                    "entry_rules": [
                        {
                            "indicator": "VWAP",
                            "params": {},
                            "condition": "greater_than",
                            "compare_to": 100,
                        }
                    ],
                    "exit_rules": [],
                },
            )
        assert exc_info.value.response.status_code == 400

    def test_invalid_timeframe_rejected(self, client):
        import httpx

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            run_backtest(
                client,
                symbol="BTC/USDT",
                timeframe="2h",
                start_date="2024-01-01",
                strategy={"name": "Test", "entry_rules": [], "exit_rules": []},
            )
        assert exc_info.value.response.status_code == 400

    def test_nonexistent_backtest_404(self, client):
        import httpx

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            get_backtest_status(client, "00000000-0000-0000-0000-000000000000")
        assert exc_info.value.response.status_code == 404
