"""Log view widget — scrolling event feed."""

from __future__ import annotations

from textual.widgets import RichLog
from textual.widget import Widget


class GameLog(RichLog):
    """Scrolling game log with Rich markup support."""

    DEFAULT_CSS = """
    GameLog {
        border: solid $accent;
        border-title-color: $text;
        scrollbar-size-vertical: 1;
        min-height: 10;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(
            highlight=True,
            markup=True,
            wrap=True,
            auto_scroll=True,
            **kwargs,
        )
        self.border_title = "event log"

    def write_game(self, block: int, message: str, style: str = "") -> None:
        """Write a game log entry with block number."""
        if style:
            self.write(f"[dim]#{block:>5}[/] [{style}]{message}[/]")
        else:
            self.write(f"[dim]#{block:>5}[/] {message}")
