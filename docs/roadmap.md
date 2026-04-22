# sudo-rug — Development Roadmap

This document tracks the planned milestone structure for sudo-rug. Only Milestone 1 is currently implemented. Everything else is design intent, subject to change.

---

## Milestone 1 — Phase 1 Hustler Vertical Slice ✅ *current*

**Goal:** Prove the game is fun at the command-line level. One playable loop from start to win/lose.

- [x] Terminal shell with command parser  
- [x] Block-tick clock (async, ~2s per block)  
- [x] Single wallet (USD + token balances)  
- [x] Meme token deployment  
- [x] Constant-product AMM pool (`x * y = k`)  
- [x] Buy / sell / add-liquidity / pull-liquidity  
- [x] Bot system (real AMM trades over N blocks)  
- [x] Heat system (accumulation per action, decay per block)  
- [x] OpSec modifier  
- [x] Status panel (capital, holdings, heat, opsec, pools, bots)  
- [x] Scrolling live event log  
- [x] Win condition: net worth ≥ $50,000  
- [x] Lose condition: Heat ≥ 100 (investigated)  
- [x] Unit tests for AMM, heat, commands, market, state  

---

## Milestone 2 — Phase 1 Depth

**Goal:** Make Phase 1 richer, more replayable, and more dangerous.

- [ ] Save / load game state (JSON serialization)
- [ ] Command history (up-arrow recall)
- [ ] Richer bot AI
  - [ ] Sell-side bots (bears)
  - [ ] Arbitrage bots (two-pool equilibrium)
  - [ ] Shill bots (tweet-style log spam that draws more bot activity)
- [ ] Heat event system
  - [ ] Random on-chain sleuth investigations
  - [ ] Close call events (near-trace, player can bribe to escape)
  - [ ] Market panic events (large sells triggered by heat spike)
- [ ] OpSec upgrade items
  - [ ] VPN: lowers heat gain on trades
  - [ ] Mixer: one-time purge of heat history
  - [ ] Burner wallet: resets OpSec penalty for rug actions
- [ ] Multiple simultaneous markets (bots choose targets)
- [ ] Audit system
  - [ ] Purchase shallow audits that reduce heat and add credibility signal
  - [ ] Audits take N blocks to complete
- [ ] Phase 1 → Phase 2 progression gate (capital threshold + reputation score)

---

## Milestone 3 — Phase 2 Architect

**Goal:** The player has capital and credibility. Now they build real protocols — and exploit them.

- [ ] Protocol deployment framework
  - [ ] Lending market (collateral ratio, borrow rate, oracle source)
  - [ ] Yield vault (underlying asset, APY, TVL display)
  - [ ] Governance token (voting power, proposal system)
- [ ] TVL tracking and display
- [ ] Yield farming loop (player and bots deposit into vaults)
- [ ] Governance system
  - [ ] Submit proposals
  - [ ] Vote manipulation (heat risk)
  - [ ] Hostile takeover mechanic
- [ ] Oracle system
  - [ ] Price oracle for each token
  - [ ] Oracle lag and manipulation vectors
- [ ] Credibility stat (public reputation that affects bot behavior and audit costs)
- [ ] Phase 2 → Phase 3 gate

---

## Milestone 4 — Phase 3 Predator

**Goal:** The player now sees the mempool. They can hunt other protocols, not just their own.

- [ ] Mempool visibility
  - [ ] Pending transaction queue visible to player
  - [ ] Frontrunning (place higher-gas trade before a target)
  - [ ] Sandwich attack (buy before, sell after a large target trade)
- [ ] Exploit mechanics
  - [ ] Oracle manipulation (move price via shallow pool, then drain a lending market)
  - [ ] Reentrancy simulation (if a protocol has a known flag, exploit it)
  - [ ] Flash loan mechanic (borrow → exploit → repay in one block)
- [ ] Target protocol scanning (`scan <protocol>` reveals risk flags)
- [ ] Governance attacks on NPC protocols
- [ ] Exit strategy mechanics (mixing, bridging simulation, layered wallet hops)
- [ ] Advanced Heat events (Interpol-tier investigations, wallet freezes)

---

## Milestone 5 — Scenario Packs

**Goal:** Recreate the feeling of real historical Web3 failures as optional scenarios.

Each scenario pack is a self-contained starting state and event schedule that recreates the dynamics of a real event — not the event itself. 

- [ ] **The DAO** — governance exploit, recursive call, hard fork decision
- [ ] **Ronin** — validator key compromise, cross-chain bridge drain, delayed detection
- [ ] **Mango Markets** — oracle manipulation, self-loan, governance hostile takeover
- [ ] **Terra / Luna** — stablecoin death spiral, bank run mechanics, ecosystem collapse
- [ ] **Curve** — reentrancy in production, emergency patches, white hat race
- [ ] **FTX** — exchange insolvency simulation, customer fund misuse, contagion

Each pack:
- Has a specific starting configuration (capital, protocols deployed, NPC activity)
- Has scripted events that fire at certain blocks or conditions
- Has a unique win/lose condition beyond the standard capital target

---

## Milestone 6 — Full Roguelite Meta-Progression

**Goal:** Multiple playthroughs with meaningful variation and carry-over progression.

- [ ] Multiple starting identities
  - **The Dev** — higher OpSec, lower starting capital, can deploy protocols earlier
  - **The Trader** — higher starting capital, lower OpSec, early bot unlock
  - **The Auditor** — credibility head start, can scan protocols from block 1, lower rug upside
  - **The Ghost** — maximum OpSec, minimum capital, no identity; heat system works differently
- [ ] Meta-progression currency (reputation carries between runs)
- [ ] Permanent unlocks (scenarios, identities, starting items)
- [ ] Leaderboard (local, tracking best net worth, lowest peak heat, fastest win)
- [ ] Challenge modes (speed run, iron wallet, no-rug pacifist, heat pinned at 50)
- [ ] Achievement system

---

## Non-Goals (permanent)

These will never be added regardless of milestone:

- Real blockchain connection
- Real money / token integration
- Multiplayer / networking
- Mobile application
- Audio (beyond terminal bell at most)
