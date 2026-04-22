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

    return messages
