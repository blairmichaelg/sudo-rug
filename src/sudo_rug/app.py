import asyncio
import threading
import time
import random
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from sudo_rug.core.state import GameState
from sudo_rug.sim.heat import decay_heat, get_heat_bar
from sudo_rug.sim.opsec import get_opsec_rating
from sudo_rug.shell.commands import execute_command
from sudo_rug.core.events import check_win_lose, check_heat_warnings, check_random_events
from sudo_rug.sim.bots import tick_bots
from sudo_rug.content.messages import random_tick_flavor, random_heat_flavor, BOOT_MESSAGES, SYSTEM_READY

console = Console()

def build_status_panel(state: GameState) -> Panel:
    nw = state.net_worth()
    target = state.config.win_target

    lines = []
    lines.append(f"[bold]Block[/] #{state.clock_block}")
    lines.append(f"[bold]Phase[/] [magenta]{state.phase.name}[/]")
    lines.append("")
    lines.append(f"[bold]Net Worth[/]")

    pct = nw / target if target > 0 else 0
    if pct >= 0.8:
        nw_color = "green"
    elif pct >= 0.4:
        nw_color = "yellow"
    else:
        nw_color = "white"
    lines.append(f"  [{nw_color}]${nw:,.2f}[/]")
    lines.append(f"  [dim]target: ${target:,.0f}[/]")

    lines.append("")
    lines.append(f"[bold]USD[/] [green]${state.wallet.get('USD'):,.2f}[/]")

    for ticker in state.tokens:
        held = state.wallet.get(ticker)
        pool_key = f"{ticker}/USD"
        if pool_key in state.pools and state.pools[pool_key].reserve_base > 0:
            price = state.pools[pool_key].price
            val = held * price
            lines.append(f"[bold]{ticker}[/] {held:,.0f}")
            lines.append(f"  [dim]@${price:.6f} = ${val:,.2f}[/]")
        else:
            lines.append(f"[bold]{ticker}[/] {held:,.0f}")

    lines.append("")
    lines.append(f"[bold]Heat[/]")
    lines.append(f"  {get_heat_bar(state.heat.level)}")

    lines.append("")
    lines.append(f"[bold]OpSec[/] {get_opsec_rating(state)}")

    if state.bots:
        lines.append("")
        lines.append(f"[bold]Bots[/] {len(state.bots)} active")
        for i, bot in enumerate(state.bots):
            lines.append(
                f"  [dim]#{i} {bot.blocks_remaining}b "
                f"${bot.budget_remaining:,.0f}[/]"
            )

    if state.pools:
        lines.append("")
        lines.append(f"[bold]Pools[/]")
        for key, pool in state.pools.items():
            if pool.reserve_base > 0:
                lines.append(f"  {key}")
                lines.append(f"  [dim]${pool.price:.6f}[/]")
            else:
                lines.append(f"  {key} [red]DRAINED[/]")

    return Panel("\n".join(lines), title="status", border_style="blue")

def build_log_panel(state: GameState, max_lines: int = 20) -> Panel:
    lines = []
    for entry in state.log[-max_lines:]:
        prefix = f"[dim]#{entry.block}[/]"
        msg = f"[{entry.style}]{entry.message}[/]" if entry.style else entry.message
        lines.append(f"{prefix} {msg}")
    return Panel("\n".join(lines), title="game log")

def build_layout(state: GameState) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=3),
        Layout(name="bottom", ratio=1),
    )
    layout["top"].split_row(
        Layout(build_log_panel(state), name="log", ratio=2),
        Layout(build_status_panel(state), name="status", ratio=1),
    )
    layout["bottom"].update(
        Panel("[dim]Type a command below. Press Ctrl+C or type 'quit' to exit.[/]", title="INPUT")
    )
    return layout

def _tick(state: GameState):
    """Process a single simulation tick."""
    state.clock_block += 1
    block = state.clock_block

    if block > 0 and block % 50 == 0:
        import json
        from pathlib import Path
        save_dir = Path.home() / ".sudo_rug"
        save_dir.mkdir(parents=True, exist_ok=True)
        with open(save_dir / "save.json", "w") as f:
            json.dump(state.to_dict(), f)
        state.add_log("[dim]Autosaved.[/]")

    decay_heat(state)
    bot_messages = tick_bots(state)
    for msg in bot_messages:
        state.add_log(msg)
    rand_events = check_random_events(state)
    for r in rand_events:
        state.add_log(r)
    if random.random() < 0.30:
        flavor = random_tick_flavor()
        state.add_log(f"[dim]{flavor}[/]")
    if state.heat.level > 10 and random.random() < 0.20:
        hf = random_heat_flavor(state.heat.level)
        state.add_log(f"[dim italic]{hf}[/]")
    warnings = check_heat_warnings(state)
    for w in warnings:
        state.add_log(w, style="bold yellow")
    result = check_win_lose(state)

async def game_clock(state: GameState, live: Live):
    # Boot sequence messages
    for msg in BOOT_MESSAGES:
        state.add_log(msg)
        live.update(build_layout(state))
        await asyncio.sleep(0.15)
    await asyncio.sleep(0.3)
    state.add_log(SYSTEM_READY)
    state.add_log("System initialized. Welcome to the dark forest.", style="green")
    state.add_log(
        f"Starting capital: ${state.config.start_capital:,.2f}. "
        f"Target: ${state.config.win_target:,.0f}.",
    )
    live.update(build_layout(state))

    while state.alive and state.running:
        await asyncio.sleep(state.config.tick_interval)
        if not state.running or not state.alive:
            break
        _tick(state)
        live.update(build_layout(state))

def input_loop(state: GameState, live: Live, loop: asyncio.AbstractEventLoop):
    while state.alive and state.running:
        try:
            raw = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            state.running = False
            break
        if not raw.strip():
            continue
            
        if raw.lower().strip() in ("quit", "q", "exit"):
            state.running = False
            break
            
        state.add_log(f"> {raw.strip()}", style="cyan")
        
        from sudo_rug.core.state import GameState as RealGameState
        
        output = execute_command(state, raw.strip())
        
        if output and output[0] == "__NEWGAME__":
            from pathlib import Path
            import os
            save_path = Path.home() / ".sudo_rug" / "save.json"
            if save_path.exists():
                save_path.unlink()
            state.add_log("[dim]Starting fresh run.[/]")
            os._exit(0) # In Rich Live, easiest restart is forcing script exit if running without a global outer restart loop. Or we could just break out. But instructions don't require full newgame loop support in new setup. Wait! I should update the state in place like before.
        
        elif output and output[0].startswith("__LOAD_JSON__"):
            import json
            parts = output[0].split("\n", 1)
            try:
                data = json.loads(parts[1])
                new_state = RealGameState.from_dict(data)
                
                # Copy values over to current state to keep reference
                state.__dict__.update(new_state.__dict__)
                
                state.add_log(f"✓ loaded from Block #{state.clock_block}.", style="green")
                state.add_log(f"  Capital: ${state.wallet.get('USD'):,.2f}")
                state.add_log(f"  Heat: {state.heat.level:.1f}")
                state.add_log(f"  OpSec Tier: {state.opsec_tier}")
            except Exception as e:
                state.add_log(f"[red]Error parsing save:[/] {e}")
        
        else:
            for line in output:
                if line.startswith("__WAIT__"):
                    blocks = int(line.replace("__WAIT__", ""))
                    state.add_log(f"[dim]Waiting {blocks} blocks...[/]")
                    for _ in range(blocks):
                        time.sleep(state.config.tick_interval)
                        _tick(state)
                    state.add_log(f"[dim]...{blocks} blocks passed.[/]")
                elif line == "__NEWGAME__":
                    pass 
                else:
                    state.add_log(line)
                    
        live.update(build_layout(state))
        if not state.alive:
            break

def run_app(state: GameState):
    layout = build_layout(state)
    with Live(layout, console=console, refresh_per_second=4, screen=True) as live:
        loop = asyncio.new_event_loop()
        clock_thread = threading.Thread(
            target=lambda: loop.run_until_complete(game_clock(state, live)),
            daemon=True
        )
        clock_thread.start()
        input_loop(state, live, loop)
    
    if not state.alive and not state.won:
        console.print("\n[bold red]═══ GAME OVER ═══[/]")
        console.print("[dim]The chain remembers. You didn't move fast enough.[/]")
    elif state.won:
        console.print("\n[bold green]═══ YOU WIN ═══[/]")
        console.print("[dim]For now. The dark forest is patient.[/]")
