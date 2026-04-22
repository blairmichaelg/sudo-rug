"""Heat system — accumulation, decay, and risk escalation."""

from __future__ import annotations

from sudo_rug.core.enums import ActionType
from sudo_rug.core.state import GameState


# Heat costs per action type
HEAT_COSTS: dict[ActionType, float] = {
    ActionType.DEPLOY_TOKEN: 10.0,
    ActionType.TRADE_BUY: 1.0,
    ActionType.TRADE_SELL: 3.0,
    ActionType.RUN_BOTS: 5.0,
    ActionType.PULL_LIQUIDITY: 50.0,
    ActionType.CREATE_POOL: 2.0,
}


def add_heat(state: GameState, action: ActionType, multiplier: float = 1.0) -> float:
    """Add heat for an action. Returns actual heat added."""
    base_cost = HEAT_COSTS.get(action, 0.0)
    # OpSec reduces heat gain: effective = base * (1.0 - opsec * 0.5)
    opsec_factor = 1.0 - (state.opsec * 0.5)
    actual = base_cost * opsec_factor * multiplier
    state.heat.level += actual
    state.heat.history.append((state.clock_block, state.heat.level))
    return actual


def decay_heat(state: GameState) -> float:
    """Decay heat by one block's worth. Returns amount decayed."""
    decay = state.config.heat_decay_per_block
    actual_decay = min(decay, state.heat.level)
    state.heat.level = max(0.0, state.heat.level - decay)
    return actual_decay


def get_heat_bar(level: float, width: int = 20) -> str:
    """Render a visual heat bar."""
    clamped = max(0.0, min(100.0, level))
    filled = int((clamped / 100.0) * width)
    empty = width - filled

    if clamped >= 75:
        color = "red"
    elif clamped >= 50:
        color = "yellow"
    elif clamped >= 25:
        color = "dark_orange"
    else:
        color = "green"

    bar = "█" * filled + "░" * empty
    return f"[{color}]{bar}[/] {clamped:.1f}/100"


def check_heat_lockdown(state: GameState, action: ActionType) -> tuple[bool, float, str | None]:
    """Check if an action is allowed given current heat, and return (allowed, penalty, message)."""
    h = state.heat.level

    if h >= 90.0:
        return False, 0.0, "[bold red]⚠ LOCKDOWN. Heat critical. Only passive actions allowed.[/]"

    penalty = 0.0
    msg = None

    if h >= 75.0:
        if action == ActionType.RUN_BOTS:
            return False, 0.0, "[red]Heat too high to hire bots. Investigators are watching bot wallets.[/]"
        if action == ActionType.DEPLOY_TOKEN:
            penalty += 5.0
            msg = "[dim]Elevated scrutiny. Deploy cost increased.[/]"

    if h >= 50.0:
        if action in (ActionType.TRADE_BUY, ActionType.TRADE_SELL):
            penalty += 1.0
            if not msg:
                msg = "[dim]Elevated scrutiny. Trade heat increased.[/]"

    return True, penalty, msg
