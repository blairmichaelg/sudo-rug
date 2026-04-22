"""Tests for the AMM math module."""

import pytest
from sudo_rug.sim.amm import calc_swap_exact_in, get_price, SwapResult


class TestGetPrice:
    def test_basic_price(self):
        # 1000 USD, 1000000 tokens -> 0.001 per token
        assert get_price(1000, 1000000) == pytest.approx(0.001)

    def test_zero_tokens(self):
        assert get_price(1000, 0) == 0.0

    def test_equal_reserves(self):
        assert get_price(500, 500) == pytest.approx(1.0)


class TestSwapExactIn:
    def test_basic_swap(self):
        """Buy tokens with 100 USD from a 1000/1000000 pool."""
        result = calc_swap_exact_in(
            amount_in=100,
            reserve_in=1000,
            reserve_out=1000000,
            fee=0.003,
        )
        assert isinstance(result, SwapResult)
        assert result.amount_in == 100
        assert result.amount_out > 0
        assert result.amount_out < 1000000  # can't drain pool
        assert result.fee_paid == pytest.approx(0.3)
        assert result.price_after < result.price_before  # buying pushes price up
        # (price is reserve_out/reserve_in so buying from out makes it less)

    def test_constant_product_holds(self):
        """k should increase (fees captured) or stay approx constant."""
        reserve_in = 1000
        reserve_out = 1000000
        k_before = reserve_in * reserve_out

        result = calc_swap_exact_in(
            amount_in=100,
            reserve_in=reserve_in,
            reserve_out=reserve_out,
            fee=0.003,
        )
        k_after = result.new_reserve_in * result.new_reserve_out
        # k should be >= k_before (fees add to reserves)
        assert k_after >= k_before

    def test_large_trade_slippage(self):
        """Large trades should have significant slippage."""
        small = calc_swap_exact_in(10, 1000, 1000000, 0.003)
        large = calc_swap_exact_in(500, 1000, 1000000, 0.003)

        # Price impact should be worse for large trade
        small_effective_price = small.amount_in / small.amount_out
        large_effective_price = large.amount_in / large.amount_out
        assert large_effective_price > small_effective_price

    def test_zero_input_raises(self):
        with pytest.raises(ValueError):
            calc_swap_exact_in(0, 1000, 1000000, 0.003)

    def test_negative_input_raises(self):
        with pytest.raises(ValueError):
            calc_swap_exact_in(-100, 1000, 1000000, 0.003)

    def test_zero_fee(self):
        result = calc_swap_exact_in(100, 1000, 1000000, 0.0)
        assert result.fee_paid == 0.0
        # Without fees, effective in = amount_in
        expected_out = (1000000 * 100) / (1000 + 100)
        assert result.amount_out == pytest.approx(expected_out)

    def test_large_trade_never_drains_pool(self):
        """Even a massive trade can't drain the pool (constant product)."""
        result = calc_swap_exact_in(
            amount_in=1_000_000,
            reserve_in=10,
            reserve_out=100,
            fee=0.0,
        )
        # Should get close to but never reach the full reserve
        assert result.amount_out < 100
        assert result.amount_out > 99  # should be very close though

    def test_symmetry(self):
        """Buying then selling should lose money (fees)."""
        # Buy
        buy = calc_swap_exact_in(100, 1000, 1000000, 0.003)
        # Sell the tokens back
        sell = calc_swap_exact_in(
            buy.amount_out,
            buy.new_reserve_out,
            buy.new_reserve_in,
            0.003,
        )
        # Should get back less than 100 due to fees + slippage
        assert sell.amount_out < 100
