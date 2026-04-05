---
description: Set up Panther — get your API key and configure the MCP server
---

Help the user set up Panther for backtesting trading strategies.

## Steps

1. **Check if PANTHER_API_KEY is already set:**
   Run `echo $PANTHER_API_KEY` to check. If it starts with `pthr_`, they're already configured — skip to step 4.

2. **Sign up for a free account:**
   Tell the user to go to https://panther.watch/register and sign up with their email. They'll get an API key starting with `pthr_`.

3. **Set the API key:**
   Tell the user to set their API key:
   ```
   export PANTHER_API_KEY=pthr_<their_key>
   ```
   Or add it to their shell profile (~/.zshrc or ~/.bashrc) for persistence.

4. **Verify the setup:**
   Use the `list_available_assets` tool to verify the connection works. If it returns a list of assets, the setup is complete.

5. **Show what they can do:**
   Suggest they try: "Backtest a golden cross strategy (SMA 50/200) on BTC/USDT over 2024"
