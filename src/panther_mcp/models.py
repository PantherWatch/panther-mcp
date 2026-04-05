from pydantic import BaseModel, Field


class IndicatorRef(BaseModel):
    indicator: str = Field(description="Indicator name: SMA, EMA, RSI, MACD, BB")
    params: dict = Field(description="Indicator parameters, e.g. {'period': 20}")


class Rule(BaseModel):
    indicator: str = Field(description="Indicator name: SMA, EMA, RSI, MACD, BB")
    params: dict = Field(description="Indicator parameters, e.g. {'period': 50}")
    condition: str = Field(
        description="Condition: crosses_above, crosses_below, greater_than, less_than, equals"
    )
    compare_to: IndicatorRef | float = Field(
        description="Compare to another indicator (e.g. {'indicator': 'SMA', 'params': {'period': 200}}) or a numeric value (e.g. 70)"
    )


class Strategy(BaseModel):
    name: str = Field(description="Human-readable strategy name")
    entry_rules: list[Rule] = Field(description="Rules that trigger entry (buy)")
    exit_rules: list[Rule] = Field(description="Rules that trigger exit (sell)")
    stop_loss: float | None = Field(
        default=None, description="Stop loss as fraction, e.g. 0.05 for 5%"
    )
    take_profit: float | None = Field(
        default=None, description="Take profit as fraction, e.g. 0.15 for 15%"
    )
