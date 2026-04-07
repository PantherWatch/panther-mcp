from typing import Literal

from pydantic import BaseModel, Field


class IndicatorRef(BaseModel):
    indicator: str = Field(
        description="Indicator name: SMA, EMA, RSI, MACD, BB, VWAP, ATR, STOCH, ADX, OBV, SUPERTREND, ICHIMOKU, WILLIAMS_R, CCI, PSAR, MFI, ROC, DONCHIAN, KELTNER, STOCH_RSI, CMF, TSI, AROON, DMI, CONNORS_RSI"
    )
    params: dict = Field(description="Indicator parameters, e.g. {'period': 20}")


class Rule(BaseModel):
    indicator: str = Field(
        description="Indicator name: SMA, EMA, RSI, MACD, BB, VWAP, ATR, STOCH, ADX, OBV, SUPERTREND, ICHIMOKU, WILLIAMS_R, CCI, PSAR, MFI, ROC, DONCHIAN, KELTNER, STOCH_RSI, CMF, TSI, AROON, DMI, CONNORS_RSI"
    )
    params: dict = Field(description="Indicator parameters, e.g. {'period': 50}")
    condition: str = Field(
        description="Condition: crosses_above, crosses_below, greater_than, less_than, equals"
    )
    compare_to: IndicatorRef | float = Field(
        description="Compare to another indicator (e.g. {'indicator': 'SMA', 'params': {'period': 200}}) or a numeric value (e.g. 70)"
    )


class Strategy(BaseModel):
    name: str = Field(description="Human-readable strategy name")
    direction: Literal["long", "short", "both"] = Field(
        default="long",
        description="Trade direction: 'long' (default), 'short', or 'both'. "
        "For 'short', entry_rules trigger short entries and exit_rules trigger short covers. "
        "For 'both', also provide short_entry_rules and short_exit_rules.",
    )
    entry_rules: list[Rule] = Field(
        description="Rules that trigger entry (buy for long, short entry when direction='short')"
    )
    exit_rules: list[Rule] = Field(
        description="Rules that trigger exit (sell for long, short cover when direction='short')"
    )
    short_entry_rules: list[Rule] | None = Field(
        default=None,
        description="Rules that trigger short entry (only when direction='both')",
    )
    short_exit_rules: list[Rule] | None = Field(
        default=None,
        description="Rules that trigger short exit / cover (only when direction='both')",
    )
    stop_loss: float | None = Field(
        default=None, description="Stop loss as fraction, e.g. 0.05 for 5%"
    )
    take_profit: float | None = Field(
        default=None, description="Take profit as fraction, e.g. 0.15 for 15%"
    )


class ParamRange(BaseModel):
    rule_path: str = Field(
        description="Path to the parameter, e.g. 'entry_rules[0].params.period'"
    )
    start: float = Field(description="Start value (inclusive)")
    end: float = Field(description="End value (inclusive)")
    step: float = Field(description="Step size")


class Constraint(BaseModel):
    left: str = Field(description="Left rule_path")
    op: Literal["<", ">", "<=", ">=", "=", "=="] = Field(description="Comparison operator")
    right: str = Field(description="Right rule_path")
