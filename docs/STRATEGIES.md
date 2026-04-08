# Panther Strategy Guide

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

### VWAP (Volume Weighted Average Price)
- params: {"period": int}
- Rolling VWAP based on typical price and volume.
- Example: {"indicator": "VWAP", "params": {"period": 20}}

### ATR (Average True Range)
- params: {"period": int}
- Measures volatility. Useful for dynamic stop losses.
- Example: {"indicator": "ATR", "params": {"period": 14}}

### STOCH (Stochastic Oscillator)
- params: {"k_period": int, "d_period": int}
- Outputs: percent_k (default), percent_d. Values 0-100. Overbought > 80, oversold < 20.
- Example: {"indicator": "STOCH", "params": {"k_period": 14, "d_period": 3}}

### ADX (Average Directional Index)
- params: {"period": int}
- Measures trend strength. Values 0-100. Strong trend > 25.
- Example: {"indicator": "ADX", "params": {"period": 14}}

### OBV (On Balance Volume)
- params: {} (no parameters)
- Cumulative volume flow. Rising OBV confirms uptrend.
- Example: {"indicator": "OBV", "params": {}}

### SUPERTREND
- params: {"period": int, "multiplier": float}
- ATR-based trend indicator. Price above = bullish, below = bearish.
- Example: {"indicator": "SUPERTREND", "params": {"period": 10, "multiplier": 3.0}}

### ICHIMOKU (Ichimoku Cloud)
- params: {"tenkan": int, "kijun": int, "senkou": int}
- Outputs: tenkan_sen (default), kijun_sen, senkou_a, senkou_b.
- Example: {"indicator": "ICHIMOKU", "params": {"tenkan": 9, "kijun": 26, "senkou": 52}}

### WILLIAMS_R (Williams %R)
- params: {"period": int}
- Values -100 to 0. Overbought > -20, oversold < -80.
- Example: {"indicator": "WILLIAMS_R", "params": {"period": 14}}

### CCI (Commodity Channel Index)
- params: {"period": int}
- Overbought > 100, oversold < -100.
- Example: {"indicator": "CCI", "params": {"period": 20}}

### PSAR (Parabolic SAR)
- params: {"af_start": float, "af_increment": float, "af_max": float}
- Trend reversal indicator. Dots above price = bearish, below = bullish.
- Example: {"indicator": "PSAR", "params": {"af_start": 0.02, "af_increment": 0.02, "af_max": 0.2}}

### MFI (Money Flow Index)
- params: {"period": int}
- Volume-weighted RSI. Values 0-100. Overbought > 80, oversold < 20.
- Example: {"indicator": "MFI", "params": {"period": 14}}

### ROC (Rate of Change)
- params: {"period": int}
- Percentage price change over N periods. Positive = upward momentum.
- Example: {"indicator": "ROC", "params": {"period": 12}}

### DONCHIAN (Donchian Channels)
- params: {"period": int}
- Outputs: upper (default), middle, lower. Highest high / lowest low over N periods.
- Example: {"indicator": "DONCHIAN", "params": {"period": 20}}

### KELTNER (Keltner Channels)
- params: {"period": int, "multiplier": float}
- Outputs: upper (default), middle, lower. EMA +/- ATR * multiplier. Popular for squeeze setups.
- Example: {"indicator": "KELTNER", "params": {"period": 20, "multiplier": 2.0}}

### STOCH_RSI (Stochastic RSI)
- params: {"rsi_period": int, "stoch_period": int}
- Stochastic oscillator applied to RSI. Values 0-100. More sensitive than plain RSI.
- Example: {"indicator": "STOCH_RSI", "params": {"rsi_period": 14, "stoch_period": 14}}

### CMF (Chaikin Money Flow)
- params: {"period": int}
- Measures buying/selling pressure. Values -1 to 1. Positive = buying pressure.
- Example: {"indicator": "CMF", "params": {"period": 20}}

### TSI (True Strength Index)
- params: {"long_period": int, "short_period": int}
- Double-smoothed momentum. Values roughly -100 to 100. Cleaner signals than MACD.
- Example: {"indicator": "TSI", "params": {"long_period": 25, "short_period": 13}}

### AROON (Aroon Indicator)
- params: {"period": int}
- Outputs: aroon_up (default), aroon_down. Measures time since highest/lowest price. Values 0-100.
- Example: {"indicator": "AROON", "params": {"period": 25}}

### DMI (Directional Movement Index)
- params: {"period": int}
- Outputs: plus_di (default), minus_di. Companion to ADX showing trend direction.
- Example: {"indicator": "DMI", "params": {"period": 14}}

### CONNORS_RSI (Connors RSI)
- params: {"rsi_period": int, "streak_period": int, "rank_period": int}
- Composite of RSI + streak RSI + ROC percentile. Popular for mean reversion.
- Example: {"indicator": "CONNORS_RSI", "params": {"rsi_period": 3, "streak_period": 2, "rank_period": 100}}

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
- A formula (see Formulas section below)

## Formulas

Rules can use **formulas** to combine indicators, price fields, and constants with arithmetic. Use `"formula"` instead of `"indicator"`/`"params"` on a rule.

### Formula Node Types

| Node | Shape | Returns |
|------|-------|---------|
| Indicator | `{"indicator": "SMA", "params": {"period": 20}}` | Indicator series |
| Constant | `{"value": 0.5}` | Numeric constant |
| Price | `{"price": "close"}` | OHLCV column (open, high, low, close, volume) |
| Binary op | `{"op": "+", "left": <node>, "right": <node>}` | Arithmetic (+, -, *, /) |
| Unary op | `{"op": "abs", "operand": <node>}` | abs or negate |

Formulas are recursive — any node can contain other nodes.

### Formula Examples

#### Price Relative Strength (close / SMA > 1.05)
```json
{
  "formula": {"op": "/", "left": {"price": "close"}, "right": {"indicator": "SMA", "params": {"period": 200}}},
  "condition": "greater_than",
  "compare_to": 1.05
}
```

#### Composite Oversold ((RSI + StochRSI) / 2 < 30)
```json
{
  "formula": {
    "op": "/",
    "left": {
      "op": "+",
      "left": {"indicator": "RSI", "params": {"period": 14}},
      "right": {"indicator": "STOCH_RSI", "params": {"rsi_period": 14, "stoch_period": 14}}
    },
    "right": {"value": 2}
  },
  "condition": "less_than",
  "compare_to": 30
}
```

#### ATR Volatility Expansion (ATR(14) > ATR(28) * 1.5)
```json
{
  "indicator": "ATR",
  "params": {"period": 14},
  "condition": "greater_than",
  "compare_to": {"op": "*", "left": {"indicator": "ATR", "params": {"period": 28}}, "right": {"value": 1.5}}
}
```

#### Bollinger %B ((close - BB_lower) / (BB_upper - BB_lower) < 0.2)
```json
{
  "formula": {
    "op": "/",
    "left": {"op": "-", "left": {"price": "close"}, "right": {"indicator": "BB", "params": {"period": 20, "std": 2.0, "output": "lower"}}},
    "right": {"op": "-", "left": {"indicator": "BB", "params": {"period": 20, "std": 2.0, "output": "upper"}}, "right": {"indicator": "BB", "params": {"period": 20, "std": 2.0, "output": "lower"}}}
  },
  "condition": "less_than",
  "compare_to": 0.2
}
```

### Notes
- Most strategies don't need formulas — use them only when you need arithmetic on indicators
- Division by zero produces NaN, which is treated as "no signal" (safe default)
- Maximum nesting depth: 10 levels
- Formulas work in both `"formula"` (left side) and `"compare_to"` (right side)
- Formulas can be mixed with plain indicator rules in the same strategy
- Formula indicator params are optimizable via `rule_path` (e.g., `entry_rules[0].formula.right.params.period`)

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

## Short Selling

Set `"direction": "short"` to short sell. Entry rules trigger short entries, exit rules trigger covers.

### RSI Overbought Short
```json
{
  "name": "RSI Overbought Short",
  "direction": "short",
  "entry_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_below", "compare_to": 70}
  ],
  "exit_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_below", "compare_to": 30}
  ],
  "stop_loss": 0.05
}
```

### Long + Short (Both Directions)

Set `"direction": "both"` and provide `short_entry_rules` and `short_exit_rules`:
```json
{
  "name": "RSI Long Short",
  "direction": "both",
  "entry_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_above", "compare_to": 30}
  ],
  "exit_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_above", "compare_to": 50}
  ],
  "short_entry_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_below", "compare_to": 70}
  ],
  "short_exit_rules": [
    {"indicator": "RSI", "params": {"period": 14}, "condition": "crosses_below", "compare_to": 50}
  ],
  "stop_loss": 0.03
}
```

## Portfolio Backtesting

Test a strategy across multiple assets with weighted capital allocation using `run_portfolio_backtest`.

### Two-Asset Portfolio
```json
{
  "assets": [
    {"symbol": "BTC/USDT", "weight": 0.6},
    {"symbol": "ETH/USDT", "weight": 0.4}
  ],
  "strategy": {
    "name": "RSI Portfolio",
    "entry_rules": [
      {"indicator": "RSI", "params": {"period": 14}, "condition": "less_than", "compare_to": 30}
    ],
    "exit_rules": [
      {"indicator": "RSI", "params": {"period": 14}, "condition": "greater_than", "compare_to": 70}
    ]
  }
}
```

- Weights must sum to 1.0
- Minimum 2 assets, maximum 20
- Same strategy is applied to all assets
- Returns portfolio-level metrics (combined Sharpe, drawdown) plus per-asset breakdowns
- All trades tagged with which asset they belong to

