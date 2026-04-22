"""Custom widgets for the game UI."""

from __future__ import annotations

from textual.widgets import Static


class HeaderBar(Static):
    """Top header bar showing game title and block number."""

    DEFAULT_CSS = """
    HeaderBar {
        dock: top;
        height: 1;
        background: $boost;
        color: $text;
        text-style: bold;
        padding: 0 2;
    }
    """

    def refresh_block(self, block: int, alive: bool, won: bool) -> None:
        if won:
            status = "[bold green]★ TARGET REACHED ★[/]"
        elif not alive:
            status = "[bold red]☠ GAME OVER ☠[/]"
        else:
            status = f"Block [cyan]#{block}[/]"

        self.update(
            f"[bold]liquidate.exe[/] v0.1  │  {status}"
        )
