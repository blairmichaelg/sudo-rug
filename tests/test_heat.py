"""Tests for the heat system."""

import pytest
from sudo_rug.core.state import GameState, GameConfig
from sudo_rug.core.enums import ActionType
from sudo_rug.sim.heat import add_heat, decay_heat, get_heat_bar, HEAT_COSTS


@pytest.fixture
def state():
    return GameState(config=GameConfig())


class TestAddHeat:
    def test_deploy_adds_heat(self, state):
        added = add_heat(state, ActionType.DEPLOY_TOKEN)
        assert added > 0
        assert state.heat.level > 0

    def test_trade_adds_heat(self, state):
        added = add_heat(state, ActionType.TRADE_BUY)
        assert added > 0

    def test_pull_liquidity_high_heat(self, state):
        added = add_heat(state, ActionType.PULL_LIQUIDITY)
        assert added >= 25  # base 30 * (1 - 0.1*0.5) = 28.5

    def test_opsec_reduces_heat(self, state):
        # Low opsec
        state.opsec = 0.1
        low_opsec = add_heat(state, ActionType.TRADE_BUY)

        # Reset
        state.heat.level = 0
        state.opsec = 0.8
        high_opsec = add_heat(state, ActionType.TRADE_BUY)

        assert high_opsec < low_opsec

    def test_heat_history_tracked(self, state):
        add_heat(state, ActionType.TRADE_BUY)
        assert len(state.heat.history) == 1

    def test_multiplier(self, state):
        normal = add_heat(state, ActionType.TRADE_BUY, multiplier=1.0)
        state.heat.level = 0
        doubled = add_heat(state, ActionType.TRADE_BUY, multiplier=2.0)
        assert doubled == pytest.approx(normal * 2)


class TestDecayHeat:
    def test_basic_decay(self, state):
        state.heat.level = 10.0
        decayed = decay_heat(state)
        assert decayed == pytest.approx(0.5)
        assert state.heat.level == pytest.approx(9.5)

    def test_no_negative_heat(self, state):
        state.heat.level = 0.1
        decay_heat(state)
        assert state.heat.level >= 0.0

    def test_zero_heat_stays_zero(self, state):
        state.heat.level = 0.0
        decay_heat(state)
        assert state.heat.level == 0.0


class TestHeatBar:
    def test_low_heat(self):
        bar = get_heat_bar(10)
        assert "green" in bar

    def test_medium_heat(self):
        bar = get_heat_bar(30)
        assert "orange" in bar

    def test_high_heat(self):
        bar = get_heat_bar(80)
        assert "red" in bar

    def test_zero(self):
        bar = get_heat_bar(0)
        assert "0.0" in bar

    def test_max(self):
        bar = get_heat_bar(100)
        assert "100.0" in bar
