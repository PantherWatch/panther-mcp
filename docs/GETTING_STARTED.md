# Getting Started with Panther

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

