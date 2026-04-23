from rich.console import Console

from sudo_rug.core.state import GameState
from sudo_rug.sim.heat import decay_heat
from sudo_rug.shell.commands import execute_command
from sudo_rug.core.events import check_win_lose, check_heat_warnings, check_random_events
from sudo_rug.sim.bots import tick_bots

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
        state.add_log("[dim][SYS] Autosaved.[/]")

    decay_heat(state)
    bot_messages = tick_bots(state)
    for msg in bot_messages:
        state.add_log(msg)
    rand_events = check_random_events(state)
    for r in rand_events:
        state.add_log(r)
    warnings = check_heat_warnings(state)
    for w in warnings:
        state.add_log(w, style="bold yellow")
    check_win_lose(state)

def _print_new_logs(state: GameState, console: Console, since: int = 0):
    """Print any log entries added since `since` index."""
    new_entries = state.log[since:]
    for entry in new_entries:
        prefix = f"[dim]#{entry.block:04d}[/] "
        if entry.style:
            console.print(f"{prefix}[{entry.style}]{entry.message}[/]")
        else:
            console.print(f"{prefix}{entry.message}")
    return len(state.log)

def get_tick_count(raw: str) -> int:
    cmd = raw.strip().lower()
    if cmd in ("help", "status", "s", "wallet", "w", "log", "l", "risk", "r", "positions", "pos", "bots list", "save", "load", "newgame", "quit", "exit", "q"):
        return 0
    if cmd.startswith("help "):
        return 0
    if cmd.startswith("wait"):
        parts = cmd.split()
        if len(parts) == 2 and parts[1].isdigit():
            return int(parts[1])
        if len(parts) == 3 and parts[1] == "--blocks" and parts[2].isdigit():
            return int(parts[2])
        return 1
    return 1

def handle_special_result(result: list[str], state: GameState, console: Console) -> bool:
    if not result:
        return False
    
    if result[0] == "__NEWGAME__":
        from pathlib import Path
        from sudo_rug.content.starter_scenarios import default_config
        fresh = GameState(config=default_config())
        state.__dict__.update(fresh.__dict__)
        save_path = Path.home() / ".sudo_rug" / "save.json"
        if save_path.exists():
            save_path.unlink()
        console.print("[green][SYS] New game started.[/]")
        return True
        
    elif result[0].startswith("__LOAD_JSON__"):
        import json
        parts = result[0].split("\n", 1)
        try:
            data = json.loads(parts[1])
            new_state = GameState.from_dict(data)
            state.__dict__.update(new_state.__dict__)
            console.print(f"[green][SYS] ✓ Loaded. Block #{state.clock_block}, "
                          f"${state.wallet.get('USD'):,.2f} USD[/]")
        except Exception as e:
            console.print(f"[red][SYS] Load error:[/] {e}")
        return True

    return False

def print_boot_banner(console: Console, state: GameState):
    console.print("sudo-rug v1.0.0 — chain sim online")
    console.print("─────────────────────────────────────────────────")
    console.print("[dim]#0000[/] [SYS] Node connected. Chain ID: 31337.")
    console.print(f"[dim]#0000[/] [SYS] Wallet initialized. Capital: ${state.config.start_capital:,.2f}.")
    console.print(f"[dim]#0000[/] [SYS] Target: ${state.config.win_target:,.2f}. Phase: {state.phase.name}.")
    console.print("[dim]#0000[/] [SYS] Type `help` to list commands.")
    console.print("─────────────────────────────────────────────────")

def run_app(state: GameState):
    console = Console()
    print_boot_banner(console, state)
    
    last_idx = len(state.log)

    while state.alive and state.running:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not raw:
            continue
            
        if raw.lower() in ("quit", "q", "exit"):
            break

        result = execute_command(state, raw)
        
        if result and handle_special_result(result, state, console):
            last_idx = len(state.log)
            continue
            
        tick_count = get_tick_count(raw)
        
        for _ in range(tick_count):
            _tick(state)
            
        last_idx = _print_new_logs(state, console, last_idx)
        
        if result:
            for line in result:
                if not line.startswith("__") and not line.startswith("[SYS] Autosaved"):
                    console.print(line)

    if state.won:
        console.print("\n[bold green]═══ YOU WIN ═══[/]")
        console.print("[dim]For now. The dark forest is patient.[/]")
    elif not state.alive:
        console.print("\n[bold red]═══ GAME OVER ═══[/]")
        console.print("[dim]The chain remembers.[/]")
