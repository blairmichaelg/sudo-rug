"""OpSec system — modifiers that affect heat gain and risk.

Future expansion: hardware/software upgrade tree.
For v0.1, OpSec is a single float (0.0–1.0).
"""

from __future__ import annotations

from sudo_rug.core.state import GameState


def get_opsec_rating(state: GameState) -> str:
    """Get a human-readable OpSec rating."""
    level = state.opsec
    if level >= 0.8:
        return f"[green]HARDENED[/] ({level:.0%})"
    elif level >= 0.5:
        return f"[yellow]MODERATE[/] ({level:.0%})"
    elif level >= 0.2:
        return f"[dark_orange]BASIC[/] ({level:.0%})"
    else:
        return f"[red]EXPOSED[/] ({level:.0%})"
