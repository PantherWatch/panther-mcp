import pytest
from pydantic import ValidationError

from panther_mcp.models import IndicatorRef, Rule, Strategy


class TestIndicatorRef:
    def test_valid_indicator(self):
        ref = IndicatorRef(indicator="SMA", params={"period": 50})
        assert ref.indicator == "SMA"
        assert ref.params == {"period": 50}

    def test_missing_indicator(self):
        with pytest.raises(ValidationError):
            IndicatorRef(params={"period": 50})

    def test_missing_params(self):
        with pytest.raises(ValidationError):
            IndicatorRef(indicator="SMA")


class TestRule:
    def test_rule_with_indicator_compare(self):
        rule = Rule(
            indicator="SMA",
            params={"period": 50},
            condition="crosses_above",
            compare_to={"indicator": "SMA", "params": {"period": 200}},
        )
        assert rule.indicator == "SMA"
        assert rule.condition == "crosses_above"
        assert isinstance(rule.compare_to, IndicatorRef)
        assert rule.compare_to.indicator == "SMA"

    def test_rule_with_numeric_compare(self):
        rule = Rule(
            indicator="RSI",
            params={"period": 14},
            condition="greater_than",
            compare_to=70,
        )
        assert rule.compare_to == 70.0

    def test_rule_with_float_compare(self):
        rule = Rule(
            indicator="RSI",
            params={"period": 14},
            condition="less_than",
            compare_to=30.5,
        )
        assert rule.compare_to == 30.5

    def test_rule_missing_indicator(self):
        with pytest.raises(ValidationError):
            Rule(params={"period": 50}, condition="crosses_above", compare_to=70)

    def test_rule_missing_condition(self):
        with pytest.raises(ValidationError):
            Rule(indicator="SMA", params={"period": 50}, compare_to=70)

    def test_rule_missing_compare_to(self):
        with pytest.raises(ValidationError):
            Rule(indicator="SMA", params={"period": 50}, condition="crosses_above")


class TestStrategy:
    def test_golden_cross_strategy(self):
        s = Strategy(
            name="Golden Cross",
            entry_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_above",
                    compare_to={"indicator": "SMA", "params": {"period": 200}},
                )
            ],
            exit_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_below",
                    compare_to={"indicator": "SMA", "params": {"period": 200}},
                )
            ],
            stop_loss=0.05,
        )
        assert s.name == "Golden Cross"
        assert len(s.entry_rules) == 1
        assert len(s.exit_rules) == 1
        assert s.stop_loss == 0.05
        assert s.take_profit is None

    def test_rsi_mean_reversion_strategy(self):
        s = Strategy(
            name="RSI Mean Reversion",
            entry_rules=[
                Rule(
                    indicator="RSI",
                    params={"period": 14},
                    condition="crosses_above",
                    compare_to=30,
                )
            ],
            exit_rules=[
                Rule(
                    indicator="RSI",
                    params={"period": 14},
                    condition="crosses_above",
                    compare_to=70,
                )
            ],
            stop_loss=0.03,
            take_profit=0.10,
        )
        assert s.stop_loss == 0.03
        assert s.take_profit == 0.10

    def test_multiple_entry_rules(self):
        s = Strategy(
            name="Multi-rule",
            entry_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_above",
                    compare_to={"indicator": "SMA", "params": {"period": 200}},
                ),
                Rule(
                    indicator="RSI",
                    params={"period": 14},
                    condition="less_than",
                    compare_to=30,
                ),
            ],
            exit_rules=[
                Rule(
                    indicator="RSI",
                    params={"period": 14},
                    condition="greater_than",
                    compare_to=70,
                ),
            ],
        )
        assert len(s.entry_rules) == 2

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            Strategy(
                entry_rules=[
                    Rule(
                        indicator="SMA",
                        params={"period": 50},
                        condition="crosses_above",
                        compare_to=70,
                    )
                ],
                exit_rules=[
                    Rule(
                        indicator="SMA",
                        params={"period": 50},
                        condition="crosses_below",
                        compare_to=70,
                    )
                ],
            )

    def test_missing_entry_rules(self):
        with pytest.raises(ValidationError):
            Strategy(
                name="Bad",
                exit_rules=[
                    Rule(
                        indicator="SMA",
                        params={"period": 50},
                        condition="crosses_below",
                        compare_to=70,
                    )
                ],
            )

    def test_missing_exit_rules(self):
        with pytest.raises(ValidationError):
            Strategy(
                name="Bad",
                entry_rules=[
                    Rule(
                        indicator="SMA",
                        params={"period": 50},
                        condition="crosses_above",
                        compare_to=70,
                    )
                ],
            )

    def test_empty_entry_rules(self):
        s = Strategy(
            name="Empty",
            entry_rules=[],
            exit_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_below",
                    compare_to=70,
                ),
            ],
        )
        assert len(s.entry_rules) == 0

    def test_stop_loss_optional(self):
        s = Strategy(
            name="No SL",
            entry_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_above",
                    compare_to=70,
                )
            ],
            exit_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_below",
                    compare_to=70,
                )
            ],
        )
        assert s.stop_loss is None
        assert s.take_profit is None

    def test_serialization_roundtrip(self):
        s = Strategy(
            name="Test",
            entry_rules=[
                Rule(
                    indicator="SMA",
                    params={"period": 50},
                    condition="crosses_above",
                    compare_to=70,
                )
            ],
            exit_rules=[
                Rule(
                    indicator="RSI",
                    params={"period": 14},
                    condition="greater_than",
                    compare_to={"indicator": "EMA", "params": {"period": 20}},
                )
            ],
            stop_loss=0.05,
            take_profit=0.15,
        )
        data = s.model_dump()
        s2 = Strategy(**data)
        assert s2.name == s.name
        assert len(s2.entry_rules) == len(s.entry_rules)
        assert s2.stop_loss == s.stop_loss

    def test_json_roundtrip(self):
        s = Strategy(
            name="Test",
            entry_rules=[
                Rule(
                    indicator="MACD",
                    params={"fast": 12, "slow": 26, "signal": 9},
                    condition="crosses_above",
                    compare_to=0,
                )
            ],
            exit_rules=[
                Rule(
                    indicator="MACD",
                    params={"fast": 12, "slow": 26, "signal": 9},
                    condition="crosses_below",
                    compare_to=0,
                )
            ],
        )
        json_str = s.model_dump_json()
        s2 = Strategy.model_validate_json(json_str)
        assert s2.name == "Test"
        assert s2.entry_rules[0].indicator == "MACD"
