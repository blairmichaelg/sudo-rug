"""Tests for market operations (buy, sell, pull liquidity)."""

import pytest
from sudo_rug.core.state import GameState, GameConfig, Pool, Token
from sudo_rug.sim.market import execute_buy, execute_sell, pull_liquidity


@pytest.fixture
def state():
    """Game state with a token and pool ready."""
    s = GameState(config=GameConfig(start_capital=10_000))
    s.tokens["TEST"] = Token(ticker="TEST", total_supply=1_000_000)
    s.wallet.credit("TEST", 1_000_000)
    pool = Pool(token="TEST", base="USD", reserve_token=500_000, reserve_base=1000)
    s.pools["TEST/USD"] = pool
    s.wallet.debit("TEST", 500_000)
    s.wallet.debit("USD", 1000)
    return s


class TestExecuteBuy:
    def test_basic_buy(self, state):
        result = execute_buy(state, "TEST/USD", 100)
        assert not isinstance(result, str)
        assert result.amount_out > 0

    def test_no_pool(self, state):
        result = execute_buy(state, "FAKE/USD", 100)
        assert isinstance(result, str)

    def test_insufficient_funds(self, state):
        result = execute_buy(state, "TEST/USD", 999_999)
        assert isinstance(result, str)
        assert "Insufficient" in result

    def test_price_increases_after_buy(self, state):
        price_before = state.pools["TEST/USD"].price
        execute_buy(state, "TEST/USD", 100)
        price_after = state.pools["TEST/USD"].price
        assert price_after > price_before


class TestExecuteSell:
    def test_basic_sell(self, state):
        result = execute_sell(state, "TEST/USD", 10_000)
        assert not isinstance(result, str)
        assert result.amount_out > 0

    def test_no_pool(self, state):
        result = execute_sell(state, "FAKE/USD", 100)
        assert isinstance(result, str)

    def test_insufficient_tokens(self, state):
        result = execute_sell(state, "TEST/USD", 999_999_999)
        assert isinstance(result, str)

    def test_price_decreases_after_sell(self, state):
        price_before = state.pools["TEST/USD"].price
        execute_sell(state, "TEST/USD", 50_000)
        price_after = state.pools["TEST/USD"].price
        assert price_after < price_before


class TestPullLiquidity:
    def test_basic_pull(self, state):
        result = pull_liquidity(state, "TEST/USD")
        assert not isinstance(result, str)
        base, tokens = result
        assert base > 0
        assert tokens > 0
        assert state.pools["TEST/USD"].reserve_base == 0

    def test_no_pool(self, state):
        result = pull_liquidity(state, "FAKE/USD")
        assert isinstance(result, str)

    def test_empty_pool(self, state):
        pull_liquidity(state, "TEST/USD")
        result = pull_liquidity(state, "TEST/USD")
        assert isinstance(result, str)
