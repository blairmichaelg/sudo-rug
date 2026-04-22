"""Bot system — simulated volume generation."""

from __future__ import annotations

import random

from sudo_rug.core.state import GameState, BotJob
from sudo_rug.sim.market import execute_buy


def create_bot_job(
    state: GameState,
    budget: float,
    duration: int,
    market_key: str,
) -> BotJob | str:
    """Create a bot job. Returns BotJob or error string."""
    if budget <= 0:
        return "Budget must be positive"
    if duration <= 0:
        return "Duration must be at least 1 block"
    if market_key not in state.pools:
        return f"No pool found for {market_key}"
    if not state.wallet.debit("USD", budget):
        return "Insufficient USD for bot budget"

    job = BotJob(
        budget_remaining=budget,
        budget_total=budget,
        blocks_remaining=duration,
        blocks_total=duration,
        market=market_key,
    )

    state.bots.append(job)
    return job


def tick_bots(state: GameState) -> list[str]:
    """Process one block of bot activity. Returns log messages."""
    messages = []
    finished = []

    for i, bot in enumerate(state.bots):
        if bot.blocks_remaining <= 0 or bot.budget_remaining <= 0:
            finished.append(i)
            continue

        # Spend a portion of remaining budget with some variance
        base_spend = bot.spend_per_block
        variance = random.uniform(0.7, 1.3)
        spend = min(base_spend * variance, bot.budget_remaining)

        if spend < 0.01:
            finished.append(i)
            continue

        # Bot executes a buy
        result = execute_buy(state, bot.market, spend, actor="bot")
        if isinstance(result, str):
            # Trade failed, skip
            finished.append(i)
            messages.append(f"  bot: trade failed on {bot.market} — {result}")
            continue

        bot.budget_remaining -= spend
        bot.blocks_remaining -= 1

        messages.append(
            f"  [cyan]bot[/]: bought {result.amount_out:.2f} on {bot.market} "
            f"for ${spend:.2f} (price: ${result.price_before:.6f} [green]▲[/] ${result.price_after:.6f})"
        )

        if bot.blocks_remaining <= 0 or bot.budget_remaining < 0.01:
            finished.append(i)

    # Remove finished bots (reverse order to preserve indices)
    for i in sorted(set(finished), reverse=True):
        if i < len(state.bots):
            bot = state.bots.pop(i)
            messages.append(
                f"  bot: job completed on {bot.market} "
                f"(spent ${bot.budget_total - bot.budget_remaining:.2f} "
                f"of ${bot.budget_total:.2f})"
            )

    # Sniper bot sell pressure (15% chance per block if active pool exists)
    if random.random() < 0.15:
        # Find active pools
        active_pools = [p for p in state.pools.values() if p.reserve_base > 0]
        if active_pools:
            pool = random.choice(active_pools)
            # Sell a random 5-20% of the token reserve
            sell_amount = pool.reserve_token * random.uniform(0.05, 0.20)
            price_before = pool.price
            base_out = sell_amount * pool.price * 0.997
            pool.reserve_token += sell_amount
            pool.reserve_base = max(0.01, pool.reserve_base - base_out)
            price_after = pool.price
            
            messages.append(
                f"  [red]sniper[/]: sold {sell_amount:.2f} on {pool.market_key} "
                f"for ${base_out:.2f} (price: ${price_before:.6f} [red]▼[/] ${price_after:.6f})"
            )

    return messages
