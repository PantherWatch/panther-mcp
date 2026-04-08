from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, Field, model_validator


class IndicatorRef(BaseModel):
    indicator: str = Field(
        description="Indicator name: SMA, EMA, RSI, MACD, BB, VWAP, ATR, STOCH, ADX, OBV, SUPERTREND, ICHIMOKU, WILLIAMS_R, CCI, PSAR, MFI, ROC, DONCHIAN, KELTNER, STOCH_RSI, CMF, TSI, AROON, DMI, CONNORS_RSI"
    )
    params: dict = Field(description="Indicator parameters, e.g. {'period': 20}")


# --- Formula node types ---


class ConstantNode(BaseModel):
    value: float = Field(description="Numeric constant, e.g. 0.5 or 1.05")


class PriceNode(BaseModel):
    price: Literal["open", "high", "low", "close", "volume"] = Field(
        description="Price field to use from OHLCV data"
    )


class BinaryOpNode(BaseModel):
    op: Literal["+", "-", "*", "/"] = Field(description="Arithmetic operator")
    left: FormulaNode = Field(description="Left operand")
    right: FormulaNode = Field(description="Right operand")


class UnaryOpNode(BaseModel):
    op: Literal["abs", "negate"] = Field(description="Unary operator")
    operand: FormulaNode = Field(description="Operand")


FormulaNode = Union[IndicatorRef, ConstantNode, PriceNode, BinaryOpNode, UnaryOpNode]
BinaryOpNode.model_rebuild()
UnaryOpNode.model_rebuild()


class Rule(BaseModel):
    indicator: str | None = Field(
        default=None,
        description="Indicator name (use this OR formula, not both): SMA, EMA, RSI, MACD, BB, VWAP, ATR, STOCH, ADX, OBV, SUPERTREND, ICHIMOKU, WILLIAMS_R, CCI, PSAR, MFI, ROC, DONCHIAN, KELTNER, STOCH_RSI, CMF, TSI, AROON, DMI, CONNORS_RSI",
    )
    params: dict | None = Field(
        default=None, description="Indicator parameters, e.g. {'period': 50}"
    )
    formula: FormulaNode | None = Field(
        default=None,
        description="Formula expression tree for combining indicators/price/constants with arithmetic. Use this OR indicator/params, not both. Example: {'op': '/', 'left': {'price': 'close'}, 'right': {'indicator': 'SMA', 'params': {'period': 200}}}",
    )
    condition: str = Field(
        description="Condition: crosses_above, crosses_below, greater_than, less_than, equals"
    )
    compare_to: IndicatorRef | FormulaNode | float = Field(
        description="Compare to an indicator, a formula, or a numeric value"
    )

    @model_validator(mode="after")
    def check_indicator_or_formula(self):
        if self.indicator and self.formula:
            raise ValueError("Cannot specify both 'indicator' and 'formula'")
        if not self.indicator and not self.formula:
            raise ValueError("Must specify either 'indicator' or 'formula'")
        if self.indicator and self.params is None:
            raise ValueError("'params' required when using 'indicator'")
        return self


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
    op: Literal["<", ">", "<=", ">=", "=", "=="] = Field(
        description="Comparison operator"
    )
    right: str = Field(description="Right rule_path")


class PortfolioAsset(BaseModel):
    symbol: str = Field(description="Asset symbol, e.g. 'BTC/USDT', 'ETH/USDT'")
    weight: float = Field(
        description="Portfolio weight (0-1). All weights must sum to 1.0",
        gt=0,
        le=1,
    )
