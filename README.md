# Panther MCP Server

**Backtest any trading strategy by describing it to Claude, ChatGPT, or Gemini.**

Panther gives your AI assistant the tools to fetch market data, run backtests, and show you the results — no code required. Just describe your strategy in plain English.

## Quick Start

### 1. Get your API key

Sign up free at [panther.watch](https://panther.watch) and copy your API key.

### 2. Install

**Claude Desktop** — add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "panther": {
      "command": "uvx",
      "args": ["panther-mcp"],
      "env": {
        "PANTHER_API_KEY": "pthr_your_key_here"
      }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add panther -e PANTHER_API_KEY=pthr_your_key -- uvx panther-mcp
```

**ChatGPT** (Pro/Team/Enterprise — Developer Mode):

Add as custom MCP server: `https://panther.watch/mcp/`

**Gemini CLI:**

```json
{"mcpServers": {"panther": {"command": "uvx", "args": ["panther-mcp"], "env": {"PANTHER_API_KEY": "pthr_..."}}}}
```

**Any MCP client** (Cline, Cursor, VS Code Copilot, etc.):

```bash
uvx panther-mcp
```

### 3. Start backtesting

Just tell your AI what strategy you want to test:

> "Backtest a golden cross strategy (SMA 50/200) on BTC/USDT over 2024"

You'll get results including return, Sharpe ratio, drawdown, every trade, and a shareable link to the full report.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_available_assets` | Browse 30+ tradeable assets (crypto, forex, commodities) |
| `get_price_data` | Fetch historical OHLCV price data with summary stats |
| `run_backtest` | Define strategy with indicators + conditions, execute backtest |
| `get_backtest_status` | Poll running backtest status + progress |
| `get_backtest_results` | Get performance metrics + shareable panther.watch link |
| `list_backtests` | View your backtest history |

## Supported Assets

| Type | Source | Examples |
|------|--------|----------|
| Crypto | Binance (CCXT) | BTC/USDT, ETH/USDT, SOL/USDT + 17 more |
| Forex | IC Markets (cTrader) | EUR/USD, GBP/USD, USD/JPY + 7 more |
| Commodities | IC Markets (cTrader) | XAU/USD (Gold), XAG/USD (Silver) |

## Supported Indicators

- **SMA** — Simple Moving Average
- **EMA** — Exponential Moving Average
- **RSI** — Relative Strength Index (0-100)
- **MACD** — Moving Average Convergence Divergence (line, signal, histogram)
- **BB** — Bollinger Bands (upper, middle, lower)

## Example Strategies

**Golden Cross:**
> "Backtest SMA 50/200 crossover on BTC/USDT daily for 2024"

**RSI Mean Reversion:**
> "Buy when RSI(14) drops below 30, sell above 70 on EUR/USD daily with 5% stop loss"

**MACD Crossover:**
> "Enter when MACD line crosses above signal line, exit on reverse, on ETH/USDT daily"

**Bollinger Band Bounce:**
> "Buy when price crosses above lower Bollinger Band, sell at upper band on gold daily"

## Shareable Results

Every backtest gets a public URL you can share on Twitter, Discord, or with your trading community:

```
https://panther.watch/backtests/<backtest-id>
```

Results include performance metrics, equity curve chart, and full trade list.

## Development

```bash
git clone https://github.com/PantherWatch/panther-mcp.git
cd panther-mcp
uv sync
PANTHER_API_KEY=pthr_... uv run panther-mcp
```

## License

MIT
