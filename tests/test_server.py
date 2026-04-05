import pytest

from panther_mcp.server import (
    GETTING_STARTED_DOC,
    STRATEGIES_DOC,
    mcp,
)


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("PANTHER_API_KEY", "pthr_testkey")


class TestServerSetup:
    def test_server_name(self):
        assert mcp.name == "Panther"

    def test_server_has_instructions(self):
        assert mcp.instructions is not None
        assert "backtest" in mcp.instructions.lower()


class TestTools:
    @pytest.mark.asyncio
    async def test_six_tools_registered(self):
        tools = await mcp.list_tools()
        assert len(tools) == 6

    @pytest.mark.asyncio
    async def test_tool_names(self):
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert names == {
            "tool_list_available_assets",
            "tool_get_price_data",
            "tool_run_backtest",
            "tool_get_backtest_status",
            "tool_get_backtest_results",
            "tool_list_backtests",
        }

    @pytest.mark.asyncio
    async def test_all_tools_have_descriptions(self):
        tools = await mcp.list_tools()
        for tool in tools:
            assert tool.description, f"{tool.name} has no description"
            assert len(tool.description) > 10, f"{tool.name} description too short"

    @pytest.mark.asyncio
    async def test_run_backtest_has_strategy_param(self):
        tools = await mcp.list_tools()
        run_bt = next(t for t in tools if t.name == "tool_run_backtest")
        schema = run_bt.parameters
        assert "strategy" in schema["properties"]
        assert "symbol" in schema["properties"]
        assert "timeframe" in schema["properties"]

    @pytest.mark.asyncio
    async def test_get_price_data_params(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "tool_get_price_data")
        schema = tool.parameters
        assert "symbol" in schema["properties"]
        assert "timeframe" in schema["properties"]
        assert "start_date" in schema["properties"]


class TestResources:
    @pytest.mark.asyncio
    async def test_two_resources_registered(self):
        resources = await mcp.list_resources()
        assert len(resources) == 2

    @pytest.mark.asyncio
    async def test_resource_uris(self):
        resources = await mcp.list_resources()
        uris = {str(r.uri) for r in resources}
        assert "panther://docs/strategies" in uris
        assert "panther://docs/getting-started" in uris

    def test_strategies_doc_has_indicators(self):
        assert "SMA" in STRATEGIES_DOC
        assert "EMA" in STRATEGIES_DOC
        assert "RSI" in STRATEGIES_DOC
        assert "MACD" in STRATEGIES_DOC
        assert "BB" in STRATEGIES_DOC

    def test_strategies_doc_has_conditions(self):
        assert "crosses_above" in STRATEGIES_DOC
        assert "crosses_below" in STRATEGIES_DOC
        assert "greater_than" in STRATEGIES_DOC
        assert "less_than" in STRATEGIES_DOC

    def test_strategies_doc_has_examples(self):
        assert "Golden Cross" in STRATEGIES_DOC
        assert "RSI Mean Reversion" in STRATEGIES_DOC

    def test_getting_started_doc_has_workflow(self):
        assert "List assets" in GETTING_STARTED_DOC
        assert "Examine data" in GETTING_STARTED_DOC
        assert "Define strategy" in GETTING_STARTED_DOC
        assert "Run backtest" in GETTING_STARTED_DOC
