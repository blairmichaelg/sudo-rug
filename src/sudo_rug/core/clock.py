"""Block clock — heartbeat of the simulation."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sudo_rug.core.state import GameState


async def run_clock(state: GameState, on_tick) -> None:
    """Run the block clock. Calls on_tick(state) each block."""
    while state.running and state.alive:
        await asyncio.sleep(state.config.tick_interval)
        if not state.running or not state.alive:
            break
        state.clock_block += 1
        await on_tick(state)
