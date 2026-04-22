import threading
import time
import random
from rich.console import Console
from rich.panel import Panel

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

def _print_new_logs(state: GameState, console: Console, since: int = 0):
    """Print any log entries added since `since` index."""
    new_entries = state.log[since:]
    for entry in new_entries:
        prefix = f"[dim]#{entry.block}[/] "
        if entry.style:
            console.print(f"{prefix}[{entry.style}]{entry.message}[/]")
        else:
            console.print(f"{prefix}{entry.message}")
    return len(state.log)

def _clock_worker(state: GameState, console: Console, stop_event: threading.Event):
    """Clock runs in background thread, prints new log entries as they appear."""
    last_log_count = len(state.log)
    while not stop_event.is_set() and state.alive and state.running:
        time.sleep(state.config.tick_interval)
        if stop_event.is_set():
            break
        _tick(state)
        last_log_count = _print_new_logs(state, console, last_log_count)

def run_app(state: GameState):
    # Print boot sequence as normal console output
    for msg in BOOT_MESSAGES:
        console.print(msg)
        time.sleep(0.08)
    console.print(SYSTEM_READY)
    console.print(f"[green]Starting capital: ${state.config.start_capital:,.2f}. "
                  f"Target: ${state.config.win_target:,.0f}.[/]")
    console.print("[dim]Type 'help' for commands. Ctrl+C to quit.[/]\n")

    # Start clock thread
    stop_event = threading.Event()
    clock_thread = threading.Thread(
        target=_clock_worker,
        args=(state, console, stop_event),
        daemon=True
    )
    clock_thread.start()

    # Input loop — runs on main thread, never interrupted
    try:
        while state.alive and state.running:
            try:
                raw = input("> ")
            except (EOFError, KeyboardInterrupt):
                break
            if not raw.strip():
                continue

            output = execute_command(state, raw.strip())

            if not output:
                continue

            if output[0] == "__NEWGAME__":
                from pathlib import Path
                from sudo_rug.content.starter_scenarios import default_config
                fresh = GameState(config=default_config())
                state.__dict__.update(fresh.__dict__)
                save_path = Path.home() / ".sudo_rug" / "save.json"
                if save_path.exists():
                    save_path.unlink()
                console.print("[green]New game started.[/]")

            elif output[0].startswith("__LOAD_JSON__"):
                import json
                parts = output[0].split("\n", 1)
                try:
                    data = json.loads(parts[1])
                    new_state = GameState.from_dict(data)
                    state.__dict__.update(new_state.__dict__)
                    console.print(f"[green]✓ Loaded. Block #{state.clock_block}, "
                                  f"${state.wallet.get('USD'):,.2f} USD[/]")
                except Exception as e:
                    console.print(f"[red]Load error: {e}[/]")

            else:
                for line in output:
                    if line.startswith("__WAIT__"):
                        blocks = int(line.replace("__WAIT__", ""))
                        console.print(f"[dim]Waiting {blocks} blocks...[/]")
                        last_count = len(state.log)
                        for _ in range(blocks):
                            time.sleep(state.config.tick_interval)
                            _tick(state)
                            last_count = _print_new_logs(state, console, last_count)
                        console.print(f"[dim]Done.[/]")
                    else:
                        console.print(line)

    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()

    if state.won:
        console.print("\n[bold green]═══ YOU WIN ═══[/]")
        console.print("[dim]For now. The dark forest is patient.[/]")
    elif not state.alive:
        console.print("\n[bold red]═══ GAME OVER ═══[/]")
        console.print("[dim]The chain remembers.[/]")
