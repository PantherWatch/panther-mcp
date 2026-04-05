---
description: Browse example trading strategies you can backtest with Panther
---

Show the user example strategies they can backtest. Use the Panther MCP tools to run any of these.

## Example Strategies

### Golden Cross (SMA 50/200)
Buy when 50-day SMA crosses above 200-day SMA, sell on the reverse.
Best for: trending markets, long-term positions.
```
"Backtest SMA 50/200 crossover on BTC/USDT daily for 2024"
```

### RSI Mean Reversion
Buy when RSI(14) drops below 30 (oversold), sell above 70 (overbought).
Best for: range-bound markets, mean-reversion.
```
"Buy when RSI(14) < 30, sell when RSI(14) > 70 on ETH/USDT daily for 2024"
```

### MACD Crossover
Enter when MACD line crosses above signal line, exit on reverse.
Best for: momentum trading, catching trend changes.
```
"Enter when MACD crosses above signal line, exit on reverse, on BTC/USDT daily for 2024"
```

### Bollinger Band Bounce
Buy at the lower band, sell at the upper band.
Best for: range-bound, mean-reversion in low-volatility periods.
```
"Buy when price crosses above lower BB, sell at upper BB on gold daily for 2024"
```

### Combined: RSI + SMA Filter
Only buy RSI oversold when price is above the 200-day SMA (uptrend filter).
```
"Buy when RSI(14) < 30 AND price > SMA(200), sell when RSI(14) > 70 on BTC/USDT daily for 2024"
```

## Supported Assets
- **Crypto**: BTC, ETH, SOL, BNB, XRP + 15 more (via Binance)
- **Forex**: EUR/USD, GBP/USD, USD/JPY + 7 more (via IC Markets)
- **Commodities**: Gold (XAU/USD), Silver (XAG/USD)

## Supported Indicators
- **SMA** — Simple Moving Average (params: period)
- **EMA** — Exponential Moving Average (params: period)
- **RSI** — Relative Strength Index (params: period, range 0-100)
- **MACD** — Moving Average Convergence Divergence (params: fast, slow, signal; outputs: macd_line, signal_line, histogram)
- **BB** — Bollinger Bands (params: period, std; outputs: upper, middle, lower)

## Tips
- Add `with 5% stop loss` to any strategy to limit downside
- Add `with 15% take profit` to lock in gains
- Compare strategies: run two backtests on the same asset/period and ask Claude to compare
- Every backtest gets a shareable URL on panther.watch
