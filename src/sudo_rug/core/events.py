"""Event system — triggers, checks, and event generation."""

from __future__ import annotations

from sudo_rug.core.enums import EventType, GamePhase
from sudo_rug.core.state import GameState
import random


def check_win_lose(state: GameState) -> EventType | None:
    """Check win/lose conditions. Returns event type or None."""
    if state.heat.level >= 100.0:
        state.alive = False
        state.add_log("[HEAT] Heat 100 — BURNED. Trace complete.", style="bold red")
        state.add_log("[SYS] All actions locked. Run terminated.", style="bold red")
        return EventType.GAME_OVER

    nw = state.net_worth()
    
    # Win / Phase Progression check
    if state.phase == GamePhase.HUSTLER and nw >= state.config.win_target:
        state.phase = GamePhase.ARCHITECT
        # MS2 specified a new target of 500k
        state.config.win_target = 500_000.0
        state.add_log(f"[SYS] Target reached. Phase: {state.phase.name} unlocked.", style="bold green")
        return EventType.WIN  # Using WIN as a trigger for the Phase-Up screen

    # Bankruptcy check — only if player has deployed something
    if len(state.tokens) > 0 and nw < 1.0:
        state.alive = False
        state.add_log(
            "[SYS] Your wallet is empty. No gas money. No exit. "
            "You're done.",
            style="bold red"
        )
        return EventType.GAME_OVER

    return None


def check_heat_warnings(state: GameState) -> list[str]:
    """Generate heat warning messages at thresholds."""
    warnings = []
    h = state.heat

    if h.level >= 25 and not h.warned_25:
        h.warned_25 = True
        warnings.append(
            "[RISK] ⚠ Whispers on CT. Someone noticed your wallet activity."
        )

    if h.level >= 50 and not h.warned_50:
        h.warned_50 = True
        warnings.append(
            "[RISK] ⚠⚠ On-chain sleuths are clustering your transactions. "
            "Your wallet is on a watchlist."
        )

    if h.level >= 75 and not h.warned_75:
        h.warned_75 = True
        warnings.append(
            "[RISK] ⚠⚠⚠ A journalist just published a thread about wallets "
            "matching your pattern. Tick tock."
        )

    return warnings


def check_random_events(state: GameState) -> list[str]:
    """Check and trigger random ambient events. Returns log messages."""
    messages = []
    
    # Needs to have deployed something or have USD to be interesting
    if not state.tokens and state.wallet.get("USD") == state.config.start_capital:
        return messages

    # MS2 RANDOM EVENTS
    h = state.heat.level
    triggered = False

    # EVENT 1 — Oracle Drift (heat >= 30, ~5% chance)
    active_pools = [p for p in state.pools.values() if p.reserve_base > 0]
    if not triggered and h >= 30 and random.random() < 0.05 and active_pools:
        pool = random.choice(active_pools)
        drift = random.uniform(0.08, 0.15) * (1 if random.random() > 0.5 else -1)
        # Apply drift by adjusting reserves (constant K shift or just price shift?)
        # Specification says "Randomly moves the price". Adjusting reserve_base is cleanest.
        old_price = pool.price
        pool.reserve_base *= (1 + drift)
        new_price = pool.price
        drift_pct = drift * 100
        messages.append(f"[MKT] Oracle drift on {pool.market_key}. Price moved {drift_pct:+.1f}%.")
        triggered = True

    # EVENT 2 — Trace Ping (heat >= 60, ~8% chance)
    if not triggered and h >= 60 and random.random() < 0.08:
        state.heat.level += 5.0
        state.opsec = max(0.0, state.opsec - 0.05)
        messages.append("[RISK] Trace ping detected. Heat +5. Cover degraded.")
        triggered = True

    # EVENT 3 — Bot Decay Spike (heat >= 40, ~10% chance)
    active_bots = [b for b in state.bots if b.blocks_remaining > 0]
    if not triggered and h >= 40 and random.random() < 0.10 and active_bots:
        bot = random.choice(active_bots)
        reduction = max(1, int(bot.blocks_remaining * 0.20))
        bot.blocks_remaining = max(0, bot.blocks_remaining - reduction)
        messages.append("[BOT] Bot activity flagged. Duration reduced.")
        triggered = True

    # Existing events (keep them but lower priority or integrate)
    if not triggered:
        # MEV Sandwich Attack
        usd = state.wallet.get("USD")
        if random.random() < 0.01 and usd > 50.0 and active_pools:
            loss = usd * random.uniform(0.01, 0.05)
            state.wallet.debit("USD", loss)
            state.heat.level += 2.0
            messages.append(f"[MKT] ⚠ [red]MEV bots frontran your activity. Lost ${loss:.2f} to slippage.[/]")
            triggered = True
        
        # Viral Tweet
        if not triggered and random.random() < 0.005 and active_pools:
            state.heat.level += 10.0
            messages.append("[HEAT] ⚠ [bold yellow]An influencer tweeted your ticker. Heat +10.0![/]")
            triggered = True
        
        # Lucky Break
        if not triggered and random.random() < 0.005:
            if state.heat.level > 20:
                state.heat.level = max(0.0, state.heat.level - 15.0)
                messages.append("[HEAT] ★ [bold green]An on-chain sleuth's thread was debunked. Heat -15.0[/]")
                triggered = True

    return messages
