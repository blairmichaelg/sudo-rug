"""Constant-product AMM math.

Pure functions — no state mutation, no side effects.
These are the building blocks that market.py uses.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SwapResult:
    """Result of a swap calculation."""
    amount_in: float
    amount_out: float
    price_before: float
    price_after: float
    fee_paid: float
    new_reserve_in: float
    new_reserve_out: float


def get_price(reserve_base: float, reserve_token: float) -> float:
    """Get current price of token in base terms."""
    if reserve_token <= 0:
        return 0.0
    return reserve_base / reserve_token


def calc_swap_exact_in(
    amount_in: float,
    reserve_in: float,
    reserve_out: float,
    fee: float = 0.003,
) -> SwapResult:
    """Calculate output for an exact input swap (constant product).

    x * y = k
    (x + dx*(1-fee)) * (y - dy) = k
    dy = y * dx*(1-fee) / (x + dx*(1-fee))
    """
    if amount_in <= 0 or reserve_in <= 0 or reserve_out <= 0:
        raise ValueError("Invalid swap parameters")

    price_before = reserve_out / reserve_in if reserve_in > 0 else 0

    fee_amount = amount_in * fee
    effective_in = amount_in - fee_amount

    amount_out = (reserve_out * effective_in) / (reserve_in + effective_in)

    new_reserve_in = reserve_in + amount_in
    new_reserve_out = reserve_out - amount_out

    price_after = new_reserve_out / new_reserve_in if new_reserve_in > 0 else 0

    return SwapResult(
        amount_in=amount_in,
        amount_out=amount_out,
        price_before=price_before,
        price_after=price_after,
        fee_paid=fee_amount,
        new_reserve_in=new_reserve_in,
        new_reserve_out=new_reserve_out,
    )


def calc_add_liquidity(
    amount_base: float,
    amount_token: float,
    reserve_base: float,
    reserve_token: float,
) -> tuple[float, float]:
    """Calculate liquidity addition. Returns (new_reserve_base, new_reserve_token)."""
    return (reserve_base + amount_base, reserve_token + amount_token)


def calc_remove_all_liquidity(
    reserve_base: float,
    reserve_token: float,
) -> tuple[float, float]:
    """Remove all liquidity. Returns (base_returned, token_returned)."""
    return (reserve_base, reserve_token)
