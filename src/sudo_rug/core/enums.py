"""Enums for game phases, event types, and other constants."""

from enum import Enum, auto


class GamePhase(Enum):
    """Player progression phases."""
    HUSTLER = auto()    # Phase 1: scraping by, deploying memes
    ARCHITECT = auto()  # Phase 2: building protocols (future)
    PREDATOR = auto()   # Phase 3: exploiting others (future)


class EventType(Enum):
    """Types of in-game events."""
    MARKET_MOVE = auto()
    BOT_TRADE = auto()
    HEAT_WARNING = auto()
    HEAT_SPIKE = auto()
    INVESTIGATION = auto()
    PLAYER_TRADE = auto()
    TOKEN_DEPLOY = auto()
    POOL_CREATED = auto()
    LIQUIDITY_PULLED = auto()
    GAME_OVER = auto()
    WIN = auto()
    SYSTEM = auto()
    BOT_STARTED = auto()
    BOT_FINISHED = auto()
    BLOCK_TICK = auto()


class ActionType(Enum):
    """Player actions that affect heat."""
    DEPLOY_TOKEN = auto()
    TRADE_BUY = auto()
    TRADE_SELL = auto()
    RUN_BOTS = auto()
    PULL_LIQUIDITY = auto()
    CREATE_POOL = auto()
