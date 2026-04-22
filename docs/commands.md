# sudo-rug — Command Reference

This is the complete reference for all currently implemented commands in sudo-rug v0.1.

---

## Global Notes

- Commands use `--flag value` syntax. Flags with no value are treated as booleans.
- Market pairs are always formatted as `TICKER/USD` (e.g. `REKT/USD`).
- All amounts are floating-point numbers.
- Rich markup (`[bold]`, `[red]`, etc.) is stripped in this document for readability.

---

## Commands

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| `help` | `help` | Show all available commands | `help` |
| `help <cmd>` | `help <command>` | Show detailed help for a specific command | `help deploy meme` |
| `status` | `status` | Show full game state: capital, holdings, pool prices, heat bar, opsec, active bots | `status` |
| `wallet` | `wallet` | Show all wallet balances (USD and all held tokens) | `wallet` |
| `deploy meme` | `deploy meme --ticker <TICKER> --supply <N>` | Deploy a new meme token. Full supply is credited to your wallet. Ticker must be 2–8 characters. | `deploy meme --ticker REKT --supply 1000000` |
| `pool create` | `pool create --token <TICKER> --base-amount <N> --token-amount <N>` | Seed a constant-product AMM pool for TICKER/USD. Debits both assets from your wallet. Initial price = base-amount / token-amount. | `pool create --token REKT --base-amount 500 --token-amount 500000` |
| `trade buy` | `trade buy --market <TICKER>/USD --amount <N>` | Buy tokens using USD. Amount is USD spent. Actual tokens received depend on pool depth and the 0.3% fee. | `trade buy --market REKT/USD --amount 100` |
| `trade sell` | `trade sell --market <TICKER>/USD --amount <N>` | Sell tokens for USD. Amount is token quantity sold. USD received depends on pool depth and the 0.3% fee. | `trade sell --market REKT/USD --amount 50000` |
| `bots run` | `bots run --budget <N> --duration <N>` | Hire bots that execute real AMM buys over N blocks. Budget is deducted immediately. Bots target the first active pool. | `bots run --budget 200 --duration 10` |
| `liquidity pull` | `liquidity pull --market <TICKER>/USD` | Pull all liquidity from a pool. Returns the full USD and token reserves to your wallet. Pool becomes inert. Adds +30 heat (reduced by OpSec). | `liquidity pull --market REKT/USD` |
| `wait` | `wait --blocks <N>` | Advance N blocks without acting. Bots trade, heat decays, events fire. Max 50 blocks per command. | `wait --blocks 5` |
| `logs` | `logs` | Show the last 20 entries from the event log with block timestamps. | `logs` |
| `quit` | `quit` | Exit the game. No save prompt. | `quit` |

---

## Heat Reference

Every player action increases Heat. At Heat = 100, you are investigated and the game ends.  
Heat decays at −0.5 per block (modified by OpSec).

| Action | Base Heat Added |
|--------|----------------|
| `deploy meme` | +5.0 |
| `pool create` | +2.0 |
| `trade buy` or `trade sell` | +1.0 |
| `bots run` | +3.0 |
| `liquidity pull` | +30.0 |
| Each block (decay) | −0.5 |

**Effective heat = base × (1.0 − opsec × 0.5)**

A player with 80% OpSec adds only 60% of the base heat cost for any action.

### Heat Warning Thresholds

Warnings fire once per game at each threshold:

| Level | Warning |
|-------|---------|
| 25 | Whispers on CT — someone noticed your wallet activity |
| 50 | On-chain sleuths clustering your transactions |
| 75 | Journalists tracking wallets matching your pattern |
| 100 | **Investigated. Game over.** |

---

## AMM Pricing Notes

Pools use the constant-product formula: **x × y = k**

- Buying tokens: you spend USD, receive tokens, price goes up
- Selling tokens: you spend tokens, receive USD, price goes down  
- Slippage is real and proportional to trade size vs pool depth
- Fees (0.3%) are captured in the pool; you recover them when pulling liquidity

**Formula for a buy:**
```
effective_in = amount_usd * (1 - 0.003)
tokens_out = (reserve_tokens * effective_in) / (reserve_usd + effective_in)
```

---

## Win / Lose Conditions

| Condition | Trigger |
|-----------|---------|
| **Win** | Net worth (USD + token holdings at current price) ≥ $50,000 |
| **Lose** | Heat level ≥ 100 |
| **Lose** | Net worth ≤ $1.00 after at least one token has been deployed |

Net worth is calculated as:
```
net_worth = wallet.USD + Σ(token_held × pool_price for each token with an active pool)
```
