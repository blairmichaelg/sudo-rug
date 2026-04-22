"""Entry point for sudo_rug."""

import sys

from sudo_rug.app import SudoRugApp
from sudo_rug.core.state import GameState
from sudo_rug.content.starter_scenarios import default_config


def main():
    """Launch the game."""
    config = default_config()
    state = GameState(config=config)
    app = SudoRugApp(state=state)
    app.run()


if __name__ == "__main__":
    main()
