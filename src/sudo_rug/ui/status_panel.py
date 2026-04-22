"""Status panel widget — sidebar showing game state."""

from __future__ import annotations

from textual.widgets import Static

from sudo_rug.core.state import GameState
from sudo_rug.sim.heat import get_heat_bar
from sudo_rug.sim.opsec import get_opsec_rating


class StatusPanel(Static):
    """Reactive status sidebar."""

    DEFAULT_CSS = """
    StatusPanel {
        width: 38;
        border: solid $accent;
        border-title-color: $text;
        padding: 1 2;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "status"

    def refresh_state(self, state: GameState) -> None:
        """Update the panel with current game state."""
        nw = state.net_worth()
        target = state.config.win_target

        lines = []
        lines.append(f"[bold]Block[/] #{state.clock_block}")
        lines.append(f"[bold]Phase[/] [magenta]{state.phase.name}[/]")
        lines.append("")
        lines.append(f"[bold]Net Worth[/]")

        # Color net worth based on progress
        pct = nw / target if target > 0 else 0
        if pct >= 0.8:
            nw_color = "green"
        elif pct >= 0.4:
            nw_color = "yellow"
        else:
            nw_color = "white"
        lines.append(f"  [{nw_color}]${nw:,.2f}[/]")
        lines.append(f"  [dim]target: ${target:,.0f}[/]")

        lines.append("")
        lines.append(f"[bold]USD[/] [green]${state.wallet.get('USD'):,.2f}[/]")

        # Token holdings
        for ticker in state.tokens:
            held = state.wallet.get(ticker)
            pool_key = f"{ticker}/USD"
            if pool_key in state.pools and state.pools[pool_key].reserve_base > 0:
                price = state.pools[pool_key].price
                val = held * price
                lines.append(f"[bold]{ticker}[/] {held:,.0f}")
                lines.append(f"  [dim]@${price:.6f} = ${val:,.2f}[/]")
            else:
                lines.append(f"[bold]{ticker}[/] {held:,.0f}")

        lines.append("")
        lines.append(f"[bold]Heat[/]")
        lines.append(f"  {get_heat_bar(state.heat.level)}")

        lines.append("")
        lines.append(f"[bold]OpSec[/] {get_opsec_rating(state)}")

        # Active bots
        if state.bots:
            lines.append("")
            lines.append(f"[bold]Bots[/] {len(state.bots)} active")
            for i, bot in enumerate(state.bots):
                lines.append(
                    f"  [dim]#{i} {bot.blocks_remaining}b "
                    f"${bot.budget_remaining:,.0f}[/]"
                )

        # Pools
        if state.pools:
            lines.append("")
            lines.append(f"[bold]Pools[/]")
            for key, pool in state.pools.items():
                if pool.reserve_base > 0:
                    lines.append(
                        f"  {key}"
                    )
                    lines.append(
                        f"  [dim]${pool.price:.6f}[/]"
                    )
                else:
                    lines.append(f"  {key} [red]DRAINED[/]")

        self.update("\n".join(lines))
