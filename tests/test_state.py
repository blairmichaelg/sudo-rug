"""Tests for the game state and win/lose conditions."""

import pytest
from sudo_rug.core.state import GameState, GameConfig, Token, Pool
from sudo_rug.core.events import check_win_lose, check_heat_warnings
from sudo_rug.core.enums import EventType


@pytest.fixture
def state():
    return GameState(config=GameConfig(start_capital=1000, win_target=50_000))


class TestNetWorth:
    def test_usd_only(self, state):
        assert state.net_worth() == pytest.approx(1000)

    def test_with_tokens(self, state):
        state.tokens["X"] = Token(ticker="X", total_supply=100)
        state.wallet.credit("X", 100)
        state.pools["X/USD"] = Pool(
            token="X", base="USD", reserve_token=100, reserve_base=1000
        )
        # tokens worth 100 * (1000/100) = 1000
        assert state.net_worth() == pytest.approx(2000)


class TestWinLose:
    def test_heat_game_over(self, state):
        state.heat.level = 100
        result = check_win_lose(state)
        assert result == EventType.GAME_OVER
        assert not state.alive

    def test_win(self, state):
        state.wallet.credit("USD", 50_000)
        result = check_win_lose(state)
        # In Milestone 2, hitting the first target triggers ARCHITECT phase and returns WIN
        assert result == EventType.WIN
        assert state.phase.name == "ARCHITECT"
        # The win_target is then upped to 500k
        assert state.config.win_target == 500_000.0
        # It's not a terminal "won = True" yet in HUSTLER -> ARCHITECT phase shift
        assert not state.won

    def test_alive_and_playing(self, state):
        result = check_win_lose(state)
        assert result is None


class TestHeatWarnings:
    def test_25_warning(self, state):
        state.heat.level = 25
        warnings = check_heat_warnings(state)
        assert len(warnings) == 1
        assert state.heat.warned_25

    def test_no_repeat(self, state):
        state.heat.level = 25
        check_heat_warnings(state)
        warnings = check_heat_warnings(state)
        assert len(warnings) == 0

    def test_multiple_thresholds(self, state):
        state.heat.level = 80
        warnings = check_heat_warnings(state)
        assert len(warnings) == 3  # 25, 50, 75 all triggered
