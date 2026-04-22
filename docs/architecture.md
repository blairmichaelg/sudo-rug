# sudo-rug — Technical Architecture

> This document describes the technical design of sudo-rug v0.1. It is intended for contributors and anyone who wants to understand how the simulation works before modifying it.

---

## Overview

sudo-rug is a terminal-native, single-player roguelite simulation of the Web3 dark forest. The player operates through a command-line interface that feels like a real terminal — not a GUI game with a terminal aesthetic painted on top.

**Design constraints that shaped everything:**
- The terminal *is* the game. No separate GUI layer.
- All feedback must be diegetic: log entries, block events, alerts, system messages.
- The simulation must feel live: prices move, bots trade, heat accumulates, between your commands.
- Simulation rules should be understandable, not a random-number curtain.

**Tech stack:**
- Python 3.11+ for modern typing and `asyncio`
- [Textual](https://textual.textualize.io/) as the TUI application framework
- [Rich](https://rich.readthedocs.io/) for all terminal formatting and markup
- `asyncio` for the concurrent simulation loop
- `pytest` + `pytest-asyncio` for testing

---

## Module Breakdown

The `src/sudo_rug/` package is divided into five layers. Dependencies only flow downward.

```
app.py  (orchestration)
  ├── shell/          (input → commands → output)
  ├── core/           (state, clock, events, enums)
  ├── sim/            (simulation logic)
  ├── ui/             (Textual widgets)
  └── content/        (text, scenarios, flavor)
```

### `core/` — Data and Time

The foundation. No simulation logic lives here.

| File | Responsibility |
|------|---------------|
| `enums.py` | `GamePhase`, `EventType`, `ActionType` enums |
| `state.py` | `GameState`, `Wallet`, `Token`, `Pool`, `BotJob`, `HeatState` dataclasses |
| `clock.py` | Async block clock driver |
| `events.py` | Win/lose condition checks, heat warning triggers |

`GameState` is the single root of all mutable game state. It is passed by reference to every subsystem. There are no global variables or singletons.

### `sim/` — Simulation Logic

Pure or near-pure business logic. Simulation modules receive `GameState` and mutate it according to defined rules.

| File | Responsibility |
|------|---------------|
| `amm.py` | **Pure** constant-product AMM math — no state, no side effects |
| `market.py` | Stateful buy/sell/pull-liquidity operations wrapping `amm.py` |
| `token_factory.py` | Token deployment validation and wallet credit |
| `bots.py` | Bot job creation and per-tick execution |
| `heat.py` | Heat accumulation per action, per-block decay, visual bar |
| `opsec.py` | OpSec rating display; extension point for upgrade tree |

### `shell/` — Command System

Handles all player input.

| File | Responsibility |
|------|---------------|
| `parser.py` | Tokenizer, flag parser, compound command resolver |
| `commands.py` | All command handler functions + the `COMMANDS` registry dict |
| `helptext.py` | Help text strings (overview + per-command detail) |

### `ui/` — Terminal Interface

All Textual widgets and screen layouts.

| File | Responsibility |
|------|---------------|
| `screens.py` | `GameScreen` — main layout: header, log, status panel, input |
| `widgets.py` | `HeaderBar` — top bar showing title and block number |
| `log_view.py` | `GameLog` — scrolling Rich log with block-numbered entries |
| `status_panel.py` | `StatusPanel` — reactive sidebar with capital, heat, pools, bots |

### `content/` — Text and Scenarios

Non-logic content: flavor text, boot messages, game configurations.

| File | Responsibility |
|------|---------------|
| `messages.py` | Boot messages, tick flavor text, heat-level ambient messages |
| `starter_scenarios.py` | `GameConfig` presets for different difficulty modes |

---

## Game Loop Design

The simulation has two concurrent execution paths:

**Path 1 — The Clock (async, background)**
```
while alive:
    await sleep(tick_interval)           # 2 seconds real-time = 1 block
    block += 1
    decay_heat(state)                    # heat falls by 0.5/block
    bot_messages = tick_bots(state)      # bots execute real AMM trades
    random_ambient_flavor()              # 30% chance of flavor text
    check_heat_warnings(state)           # trigger threshold alerts
    check_win_lose(state)                # stop the game if over
    flush_logs_to_ui()                   # sync state.log to GameLog widget
    refresh_status_panel()               # redraw sidebar
```

**Path 2 — The Command Loop (async, player-driven)**
```
player types command
→ tokenize input
→ parse flags
→ resolve command key
→ call handler(state, positionals, flags)
→ handler mutates state, returns output lines
→ output lines written to GameLog
→ status panel refreshed
```

Both paths share the same `GameState` object. Because Textual runs in a single async thread, there are no race conditions — the event loop serializes these naturally.

The `wait --blocks N` command fast-forwards the clock by calling `_tick()` N times with a short `asyncio.sleep` between each, so bots actually trade and heat actually decays during a wait.

---

## State Model

All game state lives in a single `GameState` dataclass tree. This makes the state easy to inspect, test, and eventually serialize.

```
GameState
├── config: GameConfig        (tick_interval, win_target, fees, etc.)
├── clock_block: int          (current block number)
├── wallet: Wallet            (balances: dict[str, float])
├── tokens: dict[str, Token]  (deployed tokens by ticker)
├── pools: dict[str, Pool]    (AMM pools by market key e.g. "REKT/USD")
├── heat: HeatState           (level, history, warned_* flags)
├── opsec: float              (0.0–1.0 modifier)
├── bots: list[BotJob]        (active bot tasks)
├── log: list[LogEntry]       (full scrollback history)
├── phase: GamePhase          (HUSTLER / ARCHITECT / PREDATOR)
├── alive: bool
├── won: bool
└── running: bool
```

`Wallet` provides `get(currency)`, `credit(currency, amount)`, and `debit(currency, amount) → bool` methods. `debit` returns `False` if the balance is insufficient — callers handle the refund.

`Pool` is a plain dataclass with computed properties `price` (= reserve_base / reserve_token) and `k` (constant product). All pool mutation happens in `sim/market.py`.

---

## Command System Design

The command system is intentionally minimal — no `argparse`, no `click`, no decorators.

**Parsing pipeline:**
```
raw string
  → shlex.split()              # handles quoted strings correctly
  → parse_args()               # separates positionals from --flag value pairs
  → resolve_command()          # "deploy meme" → "deploy_meme"
  → COMMANDS["deploy_meme"]    # dict lookup
  → handler(state, pos, flags) # called with parsed args
```

**`--flag` format:** Flags use `--` prefix. Values are the next token. Flags with no following value are treated as booleans (`"true"`). Hyphens in flag names are normalized to underscores (`--base-amount` → `flags["base_amount"]`).

**Adding a command** requires three things:
1. A handler function `cmd_<name>(state, pos, flags) → list[str]`
2. An entry in the `COMMANDS` dict in `commands.py`
3. A help string in `helptext.py`

No reflection, no magic, no metaclasses.

---

## AMM Simulation

The AMM uses the standard constant-product formula: **x × y = k**

```python
# Buying tokens with USD:
fee_amount = amount_in * fee          # 0.3% by default
effective_in = amount_in - fee_amount
amount_out = (reserve_out * effective_in) / (reserve_in + effective_in)
```

Key properties:
- **Slippage is real and emergent** — larger trades move price more relative to pool depth
- **Fees accumulate in the pool** — the LP (player) captures fees when pulling liquidity
- **The pool can never be drained** — the formula approaches but never reaches zero
- **Price after a trade** is `new_reserve_base / new_reserve_token`

The AMM math lives in `sim/amm.py` as pure functions. `sim/market.py` wraps these with wallet debits/credits and pool reserve updates. This separation makes the math trivially testable.

---

## Heat System

Heat is the primary risk mechanic. It accumulates from player actions and decays over time.

**Accumulation:**
```python
effective_heat = base_cost[action] * (1.0 - opsec * 0.5)
state.heat.level += effective_heat
```

**Base costs:**

| Action | Base Heat |
|--------|----------|
| Deploy token | 5.0 |
| Create pool | 2.0 |
| Trade | 1.0 |
| Run bots | 3.0 |
| Pull liquidity | 30.0 |

**Decay:** −0.5 per block, clamped at 0.

**OpSec factor:** A player with 80% OpSec adds only 60% of the base heat from any action.

**Thresholds:** Warning events fire at 25, 50, and 75. Each fires once per game. At 100, `alive = False` and the game ends.

---

## Rendering Model

```
┌─────────────────────── HEADER BAR ────────────────────────────┐
│ liquidate.exe v0.1  │  Block #1337                            │
├────────────────────────────────────┬──────────────────────────┤
│                                    │  Block #1337             │
│  GAME LOG (scrolling)              │  Phase HUSTLER           │
│  #  42  bot: bought 1,200 tokens   │                          │
│  #  43  ⚠ CT is watching          │  Net Worth               │
│  #  44  mempool quiet              │    $14,832.00            │
│  #  45  bot: job completed         │    target: $50,000       │
│                                    │                          │
│                                    │  USD  $9,400.00          │
│                                    │  REKT 583,124            │
│                                    │    @$0.0014 = $832       │
│                                    │                          │
│                                    │  Heat                    │
│                                    │  ███░░░░░░░░ 32/100      │
│                                    │  OpSec BASIC (10%)       │
│                                    │                          │
│                                    │  Bots: 1 active          │
├────────────────────────────────────┴──────────────────────────┤
│  > █                                                          │
└───────────────────────────────────────────────────────────────┘
```

- **`GameLog`** extends Textual's `RichLog` — auto-scrolling, Rich markup, block-stamped entries
- **`StatusPanel`** extends `Static` — refreshes on every tick and every command
- **`HeaderBar`** shows the game title and current block; updates on win/lose

All content uses Rich markup strings (`[bold red]`, `[green]`, `[dim]`). No raw ANSI codes anywhere. Output from command handlers is a `list[str]`, where each string may contain Rich markup.

---

## Future Extension Points

The following extension points are deliberately designed in but not implemented yet.

### Event Pack System
`core/events.py` has `EventType` enum and a `check_win_lose` / `check_heat_warnings` structure. A scenario event system can be added by:
- Defining new `EventType` variants
- Writing trigger functions that check `GameState` conditions
- Registering them in a per-tick `check_events(state)` call in `app.py`

### Upgrade Tree (OpSec / Hardware)
`sim/opsec.py` is already separated. Add `sim/upgrades.py` with purchasable items that set `state.opsec` or add other modifiers. The `status` command and `StatusPanel` already display `state.opsec`.

### Audit System
Add `sim/audits.py`. Audits reduce Heat and unlock credibility signals that suppress bot suspicion. They cost USD and take N blocks to complete (model as a timed `BotJob`-style structure).

### Mempool Visibility
Add `sim/mempool.py` as a queue of pending transactions. On each tick, bots place "pending" trades visible to the player who can then frontrun, sandwich, or block them.

### Protocol Deployment (Phase 2)
Generalize `sim/token_factory.py` into a `sim/protocol_factory.py` that can deploy lending markets, vaults, and other structures with configurable parameters (collateral ratio, borrow rate, oracle source).

### Phase Gating
`core/enums.GamePhase` already has `ARCHITECT` and `PREDATOR`. Commands and content can check `state.phase` to gate features behind phase transitions.

### Save / Load
`GameState` is a dataclass tree with only primitive types, `list`, `dict`, and other dataclasses — it can be serialized cleanly to JSON with a small custom encoder. Add `core/persistence.py`.

### Scenario Engine
`content/starter_scenarios.py` provides `GameConfig` objects. A YAML/JSON scenario loader would allow scenario packs (difficulty settings, starting conditions, event probabilities) without code changes.
