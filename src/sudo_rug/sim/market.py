"""Market operations — wraps AMM math with state mutations."""

from __future__ import annotations

from sudo_rug.core.state import GameState, Pool
from sudo_rug.sim.amm import calc_swap_exact_in, SwapResult


def execute_buy(
    state: GameState,
    market_key: str,
    usd_amount: float,
    actor: str = "player",
) -> SwapResult | str:
    """Buy tokens with USD. Returns SwapResult or error string."""
    pool = state.pools.get(market_key)
    if pool is None:
        return f"No pool found for {market_key}"

    if actor == "player" and not state.wallet.debit("USD", usd_amount):
        return "Insufficient USD balance"

    try:
        result = calc_swap_exact_in(
            amount_in=usd_amount,
            reserve_in=pool.reserve_base,
            reserve_out=pool.reserve_token,
            fee=state.config.trade_fee,
        )
    except ValueError as e:
        # Refund on failure
        if actor == "player":
            state.wallet.credit("USD", usd_amount)
        return str(e)

    pool.reserve_base = result.new_reserve_in
    pool.reserve_token = result.new_reserve_out

    if actor == "player":
        state.wallet.credit(pool.token, result.amount_out)

    return result


def execute_sell(
    state: GameState,
    market_key: str,
    token_amount: float,
    actor: str = "player",
) -> SwapResult | str:
    """Sell tokens for USD. Returns SwapResult or error string."""
    pool = state.pools.get(market_key)
    if pool is None:
        return f"No pool found for {market_key}"

    if actor == "player":
        if not state.wallet.debit(pool.token, token_amount):
            return f"Insufficient {pool.token} balance"

    try:
        result = calc_swap_exact_in(
            amount_in=token_amount,
            reserve_in=pool.reserve_token,
            reserve_out=pool.reserve_base,
            fee=state.config.trade_fee,
        )
    except ValueError as e:
        if actor == "player":
            state.wallet.credit(pool.token, token_amount)
        return str(e)

    pool.reserve_token = result.new_reserve_in
    pool.reserve_base = result.new_reserve_out

    if actor == "player":
        state.wallet.credit("USD", result.amount_out)

    return result


def pull_liquidity(
    state: GameState,
    market_key: str,
) -> tuple[float, float] | str:
    """Pull all liquidity from a pool. Returns (base, token) or error."""
    pool = state.pools.get(market_key)
    if pool is None:
        return f"No pool found for {market_key}"

    base_out = pool.reserve_base
    token_out = pool.reserve_token

    if base_out <= 0 and token_out <= 0:
        return "Pool is already empty"

    state.wallet.credit("USD", base_out)
    state.wallet.credit(pool.token, token_out)

    pool.reserve_base = 0.0
    pool.reserve_token = 0.0

    return (base_out, token_out)
