<!-- Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Built with Textual](https://img.shields.io/badge/Built%20with-Textual-6200EE?logo=python)](https://textual.textualize.io/)
[![Rich](https://img.shields.io/badge/Styled%20with-Rich-4A90D9)](https://rich.readthedocs.io/)

```
 _               _                              
| |             | |                             
| |  _   _    __| |  ___      _ __   _   _   __ _ 
| | | | | |  / _` | / _ \   | '__| | | | | / _` |
|_| | |_| | | (_| || (_) |  | |    | |_| || (_| |
(_)  \__,_|  \__,_| \___/   |_|     \__,_| \__, |
                                             __/ |
         liquidate.exe                      |___/ 
```

# sudo-rug

> **A terminal-native Web3 dark-forest management sim. Deploy tokens. Manipulate markets. Manage Heat. Get out before they find you.**

---

## What is this?

sudo-rug is a single-player roguelite that runs entirely inside your terminal. You play as an anonymous operator in a fictional on-chain dark forest — a world of meme tokens, predatory bots, shallow audits, and paranoid OpSec.

You start broke with one wallet, a small seed of capital, and access to a simulated DEX. You can deploy a token, seed a liquidity pool, hire bots to pump volume, trade the market, and decide whether to build something real or pull the rug and run. The world runs on block ticks. Markets move. Heat accumulates. Investigators close in.

The game is not a hacking simulator. It's not a joke. It's a cynical, technically-grounded sim of how the actual on-chain dark forest works — stripped to its mechanics, made playable, and shipped as a terminal application. There is no real blockchain. There is no real money. Everything is simulated.

Target: hit $50,000 net worth before your Heat hits 100. Simple premise. Dark execution.

---

## Features

### ✅ Implemented (Phase 1 — current)

- **Terminal shell** — full command-line interface with a custom parser, help system, and command history
- **Block clock** — async world simulation advancing on block ticks (~2s each); bots and market activity run concurrently
- **Wallet system** — single wallet tracking USD and all deployed token balances in real time
- **Token deployment** — deploy meme tokens with custom tickers and supply
- **Constant-product AMM** — real `x * y = k` math, real slippage, real fee capture (0.3%)
- **Liquidity pools** — seed pools, trade against them, watch price impact happen
- **Bot system** — spend budget to hire bots that execute real AMM trades over N blocks, pumping price
- **Heat system** — every action adds Heat; Heat decays per block; cross thresholds and the world notices you
- **OpSec modifier** — reduces effective heat gain from all actions
- **Status panel** — live sidebar showing capital, holdings, pool prices, Heat bar, OpSec rating, active bots
- **Scrolling event log** — diegetic terminal feed of block events, bot trades, market moves, and alerts
- **Win/lose conditions** — hit the capital target to win; let Heat reach 100 and you're done

### 🔜 Planned (Milestone 2+)

- Save / load game state
- Richer bot AI (sell-side bots, MEV bots, arbitrageurs)
- Heat events (investigations, close calls, bribe opportunities)
- OpSec upgrade items (VPN, mixer, burner wallets)
- Audit system (pay for shallow audits that reduce Heat and unlock credibility)
- Command history + tab completion
- Multiple simultaneous markets
- Phase 2: protocol deployment, lending markets, TVL farming
- Phase 3: mempool visibility, exploits, governance attacks, flash loans
- Scenario packs: inspired by DAO hack, Ronin, Mango, Terra, FTX-style failures

---

## Demo

```
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓                                     ▓
▓     liquidate.exe  v0.1              ▓
▓     sudo_rug terminal interface      ▓
▓                                     ▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

    Block #0 | Capital: $1,000.00 | Heat: 0.0

> deploy meme --ticker REKT --supply 1000000
✓ Deployed REKT — supply: 1,000,000
  Heat +4.8

> pool create --token REKT --base-amount 500 --token-amount 500000
✓ Pool REKT/USD created
  Initial price: $0.001000 | Heat +1.9

> bots run --budget 200 --duration 10
✓ Bots deployed on REKT/USD
  Budget: $200.00 over 10 blocks (~$20.00/block)
  Heat +2.9

   #   11  bot: bought 18,432.10 on REKT/USD for $20.00 (price: $0.001094)
   #   12  bot: bought 16,891.44 on REKT/USD for $20.00 (price: $0.001197)
   #   13  ⚠ Whispers on CT. Someone noticed your wallet activity.

> liquidity pull --market REKT/USD
☠ RUG EXECUTED on REKT/USD
  Recovered: $684.32 USD + 423,184 tokens
  Heat +28.5 ⚠
```

*[Full screenshot / recording coming — contributions welcome]*

---

## Setup & Install

### Requirements

- Python 3.11 or higher
- A terminal that supports ANSI colors (Windows Terminal, iTerm2, any modern Linux terminal)

### Install

```bash
# Clone the repo
git clone https://github.com/blairmichaelg/sudo-rug.git
cd sudo-rug

# Create a virtual environment (recommended)
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# Install the package and dependencies
pip install -e .
```

### Run

```bash
sudo-rug
```

Or directly:

```bash
python -m sudo_rug
```

---

## Command Reference

| Command | Syntax | Description |
|---------|--------|-------------|
| `help` | `help` or `help <command>` | Show all commands or detailed help for one |
| `status` | `status` | Show game state: capital, holdings, heat, opsec, pools, bots |
| `wallet` | `wallet` | Show wallet balances for all currencies |
| `deploy meme` | `deploy meme --ticker <X> --supply <N>` | Deploy a new meme token to your wallet |
| `pool create` | `pool create --token <X> --base-amount <N> --token-amount <N>` | Seed a TICKER/USD AMM pool |
| `trade buy` | `trade buy --market <X>/USD --amount <N>` | Buy tokens with USD |
| `trade sell` | `trade sell --market <X>/USD --amount <N>` | Sell tokens for USD |
| `bots run` | `bots run --budget <N> --duration <N>` | Hire bots to generate volume over N blocks |
| `liquidity pull` | `liquidity pull --market <X>/USD` | Pull all liquidity from a pool (rug) |
| `wait` | `wait --blocks <N>` | Advance N blocks; bots trade, heat decays |
| `logs` | `logs` | Show the last 20 event log entries |
| `quit` | `quit` | Exit the game |

### Heat Reference

Every action increases your Heat level (0–100). At 100, investigators trace your wallet. Game over.

| Action | Base Heat Added |
|--------|----------------|
| Deploy token | +5 |
| Create pool | +2 |
| Trade | +1 |
| Run bots | +3 |
| Pull liquidity (rug) | +30 |
| Each block (decay) | −0.5 |

Heat gain is reduced by your OpSec rating: `effective_heat = base * (1.0 - opsec * 0.5)`

---

## Phase Roadmap

### Phase 1 — Hustler *(current)*
You are anonymous, broke, and scraping. Deploy meme tokens, seed pools, pump with bots, trade, and decide whether to build or rug. Hit $50k before Heat hits 100. The world is indifferent to your survival.

### Phase 2 — Architect *(planned)*
You have capital and credibility. Deploy lending protocols, farming vaults, synthetic assets. Manage TVL. Attract yield chasers. Governance is now a weapon. You can audit other protocols — or exploit them.

### Phase 3 — Predator *(planned)*
You have access to the mempool. You see trades before they land. Flash loans, oracle manipulation, governance takeovers, and coordinated exploits are all possible. The dark forest hunts you and you hunt others. Events inspired by real protocol failures: DAO, Ronin, Mango, Terra, Curve, FTX.

---

## Contributing

Contributions are welcome, especially for:
- **Bug fixes** — if something doesn't behave like the sim rules say it should
- **Balance tuning** — heat costs, bot behavior, decay rates
- **New commands** — anything that extends the Phase 1 gameplay loop
- **New event packs** — scenarios, market events, heat triggers
- **Tests** — more coverage of edge cases is always good

### Local Setup

```bash
git clone https://github.com/blairmichaelg/sudo-rug.git
cd sudo-rug
python -m venv .venv && source .venv/bin/activate  # or Activate.ps1 on Windows
pip install -e ".[dev]"
python -m pytest tests/ -v
```

### PR Guidelines

- Keep PRs focused. One change per PR.
- Run tests before submitting. Don't break the test suite.
- If you're adding a new command, add a test for it in `tests/test_commands.py`.
- No framework creep. Keep modules small and the abstraction count low.

---

## Disclaimer

**sudo-rug is a fictional simulation game.**

No real blockchain is connected. No real tokens exist. No real money changes hands. All markets, prices, bots, and events are entirely simulated. Any resemblance to real protocols, exploits, or events is for game design purposes only and not an endorsement of or instruction in any real-world activity.

---

## License

[MIT](LICENSE) © 2026 Michael Blair
