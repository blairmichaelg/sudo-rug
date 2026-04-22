"""Textual screens for the game."""

from __future__ import annotations

from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Footer

from sudo_rug.ui.widgets import HeaderBar
from sudo_rug.ui.log_view import GameLog
from sudo_rug.ui.status_panel import StatusPanel


class GameScreen(Screen):
    """Main game screen layout."""

    DEFAULT_CSS = """
    GameScreen {
        layout: vertical;
    }

    #main-container {
        height: 1fr;
    }

    #log-container {
        width: 1fr;
    }

    #command-input {
        dock: bottom;
        margin: 0 0;
    }
    """

    def compose(self):
        yield HeaderBar(id="header")
        with Horizontal(id="main-container"):
            with Vertical(id="log-container"):
                yield GameLog(id="game-log")
            yield StatusPanel(id="status-panel")
        yield Input(
            placeholder="> enter command (type 'help' for commands)",
            id="command-input",
        )
