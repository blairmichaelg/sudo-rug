"""Core game state dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from sudo_rug.core.enums import GamePhase


@dataclass
class GameConfig:
    """Tunable game parameters."""
    start_capital: float = 1000.0
    win_target: float = 50_000.0
    tick_interval: float = 1.5  # seconds per block
    heat_decay_per_block: float = 0.5
    trade_fee: float = 0.003  # 0.3%
    starting_opsec: float = 0.1


@dataclass
class Token:
    """A deployed token."""
    ticker: str
    total_supply: float
    deployer: str = "player"
    block_created: int = 0


@dataclass
class Pool:
    """A constant-product AMM pool."""
    token: str        # token ticker
    base: str         # base currency (USD)
    reserve_token: float = 0.0
    reserve_base: float = 0.0

    @property
    def k(self) -> float:
        return self.reserve_token * self.reserve_base

    @property
    def price(self) -> float:
        if self.reserve_token == 0:
            return 0.0
        return self.reserve_base / self.reserve_token

    @property
    def market_key(self) -> str:
        return f"{self.token}/USD"


@dataclass
class BotJob:
    """An active bot task."""
    budget_remaining: float
    budget_total: float
    blocks_remaining: int
    blocks_total: int
    market: str  # market key e.g. "REKT/USD"
    spend_per_block: float = 0.0

    def __post_init__(self):
        if self.blocks_remaining > 0:
            self.spend_per_block = self.budget_remaining / self.blocks_remaining


@dataclass
class LogEntry:
    """A single log entry."""
    block: int
    message: str
    style: str = ""  # Rich markup style


@dataclass
class Wallet:
    """Player wallet."""
    balances: dict[str, float] = field(default_factory=lambda: {"USD": 0.0})

    def get(self, currency: str) -> float:
        return self.balances.get(currency, 0.0)

    def credit(self, currency: str, amount: float) -> None:
        self.balances[currency] = self.balances.get(currency, 0.0) + amount

    def debit(self, currency: str, amount: float) -> bool:
        current = self.balances.get(currency, 0.0)
        if current < amount:
            return False
        self.balances[currency] = current - amount
        return True


@dataclass
class HeatState:
    """Heat tracking."""
    level: float = 0.0
    history: list[tuple[int, float]] = field(default_factory=list)
    warned_25: bool = False
    warned_50: bool = False
    warned_75: bool = False


@dataclass
class GameState:
    """Root game state container."""
    config: GameConfig = field(default_factory=GameConfig)
    clock_block: int = 0
    wallet: Wallet = field(default_factory=Wallet)
    tokens: dict[str, Token] = field(default_factory=dict)
    pools: dict[str, Pool] = field(default_factory=dict)
    heat: HeatState = field(default_factory=HeatState)
    opsec: float = 0.1
    bots: list[BotJob] = field(default_factory=list)
    log: list[LogEntry] = field(default_factory=list)
    phase: GamePhase = GamePhase.HUSTLER
    alive: bool = True
    won: bool = False
    running: bool = True

    def __post_init__(self):
        self.wallet.balances["USD"] = self.config.start_capital
        self.opsec = self.config.starting_opsec

    def net_worth(self) -> float:
        """Calculate total net worth in USD."""
        total = self.wallet.get("USD")
        for ticker, token in self.tokens.items():
            pool_key = f"{ticker}/USD"
            if pool_key in self.pools:
                pool = self.pools[pool_key]
                held = self.wallet.get(ticker)
                total += held * pool.price
        return total

    def add_log(self, message: str, style: str = "") -> None:
        """Append a log entry."""
        entry = LogEntry(block=self.clock_block, message=message, style=style)
        self.log.append(entry)
