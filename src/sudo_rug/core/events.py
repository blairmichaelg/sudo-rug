"""Event system — triggers, checks, and event generation."""

from __future__ import annotations

from sudo_rug.core.enums import EventType
from sudo_rug.core.state import GameState
import random


def check_win_lose(state: GameState) -> EventType | None:
    """Check win/lose conditions. Returns event type or None."""
    if state.heat.level >= 100.0:
        state.alive = False
        state.add_log(
            "▓▓▓ INVESTIGATION COMPLETE. Your wallets have been traced. "
            "Authorities notified. Game over. ▓▓▓",
            style="bold red"
        )
        return EventType.GAME_OVER

    nw = state.net_worth()
    if nw >= state.config.win_target:
        state.won = True
        state.running = False
        state.add_log(
            f"★ NET WORTH: ${nw:,.2f} — Target reached. "
            f"You made it out. For now. ★",
            style="bold green"
        )
        return EventType.WIN

    # Bankruptcy check — only if player has deployed something
    if len(state.tokens) > 0 and nw < 1.0:
        state.alive = False
        state.add_log(
            "Your wallet is empty. No gas money. No exit. "
            "You're done.",
            style="bold red"
        )
        return EventType.GAME_OVER

    return None


def check_heat_warnings(state: GameState) -> list[str]:
    """Generate heat warning messages at thresholds."""
    warnings = []
    h = state.heat

    if h.level >= 25 and not h.warned_25:
        h.warned_25 = True
        warnings.append(
            "⚠ Whispers on CT. Someone noticed your wallet activity."
        )

    if h.level >= 50 and not h.warned_50:
        h.warned_50 = True
        warnings.append(
            "⚠⚠ On-chain sleuths are clustering your transactions. "
            "Your wallet is on a watchlist."
        )

    if h.level >= 75 and not h.warned_75:
        h.warned_75 = True
        warnings.append(
            "⚠⚠⚠ A journalist just published a thread about wallets "
            "matching your pattern. Tick tock."
        )

    return warnings


def check_random_events(state: GameState) -> list[str]:
    """Check and trigger random ambient events. Returns log messages."""
    messages = []
    
    # Needs to have deployed something or have USD to be interesting
    if not state.tokens and state.wallet.get("USD") == state.config.start_capital:
        return messages

    roll = random.random()
    
    # 2% chance per block for something bad/good to happen
    if roll < 0.01:
        # MEV Sandwich Attack (-1 to 5% of USD)
        usd = state.wallet.get("USD")
        if usd > 10.0:
            loss = usd * random.uniform(0.01, 0.05)
            state.wallet.debit("USD", loss)
            messages.append(f"⚠ [red]MEV bots frontran your activity. Lost ${loss:.2f} to slippage.[/]")
    elif roll < 0.015:
        # Viral Tweet (Heat +10, if a pool exists, fake volume)
        from sudo_rug.sim.heat import add_heat
        # avoid circular imports for add_heat if possible... actually do it this way:
        state.heat.level += 10.0
        messages.append("⚠ [bold yellow]An influencer tweeted your ticker. Heat +10.0![/]")
    elif roll < 0.02:
        # Lucky break (Heat -15)
        if state.heat.level > 20:
            state.heat.level = max(0.0, state.heat.level - 15.0)
            messages.append("★ [bold green]An on-chain sleuth's thread was debunked. Heat -15.0[/]")

    return messages
