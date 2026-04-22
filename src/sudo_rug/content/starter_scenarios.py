"""Starter scenarios and game configurations."""

from __future__ import annotations

from sudo_rug.core.state import GameConfig


def default_config() -> GameConfig:
    """Standard v0.1 game configuration."""
    return GameConfig(
        start_capital=1000.0,
        win_target=50_000.0,
        tick_interval=2.0,
        heat_decay_per_block=0.5,
        trade_fee=0.003,
        starting_opsec=0.1,
    )


def easy_config() -> GameConfig:
    """Easier config for testing."""
    return GameConfig(
        start_capital=5000.0,
        win_target=25_000.0,
        tick_interval=1.0,
        heat_decay_per_block=1.0,
        trade_fee=0.001,
        starting_opsec=0.3,
    )
