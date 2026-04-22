"""Event system — triggers, checks, and event generation."""

from __future__ import annotations

from sudo_rug.core.enums import EventType
from sudo_rug.core.state import GameState


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
