from rich.console import Console

from sudo_rug.core.state import GameState
from sudo_rug.sim.heat import decay_heat
from sudo_rug.shell.commands import execute_command
from sudo_rug.core.events import check_win_lose, check_heat_warnings, check_random_events
from sudo_rug.core.enums import GamePhase
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
        # entry.message already starts with [TAG]
        msg = entry.message
        tag = ""
        content = msg
        if msg.startswith("[") and "]" in msg:
            end_idx = msg.find("]") + 1
            tag = msg[:end_idx]
            content = msg[end_idx:].strip()
        
        formatted_line = f"{tag} [dim]#{entry.block:04d}[/] {content}"
        if entry.style:
            console.print(f"[{entry.style}]{formatted_line}[/]")
        else:
            console.print(formatted_line)
    return len(state.log)

def get_tick_count(raw: str) -> int:
    tokens = raw.strip().lower().split()
    if not tokens: return 0
    cmd = tokens[0]
    # Commands that do NOT advance the block
    if cmd in ("help", "status", "s", "wallet", "w", "log", "l", "risk", "r", "positions", "pos", "bots", "save", "load", "newgame", "quit", "exit", "q", ".", "$", "/", "!", "wait"):
        if cmd == "wait" or cmd == "w":
            if len(tokens) >= 2 and tokens[1].isdigit():
                return int(tokens[1])
            return 0 # If w or wait with no args, it returns 0 and command handler returns __WAIT__1
        return 0
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
        
        is_wait = False
        wait_blocks = 0
        if result and any(line.startswith("__WAIT__") for line in result):
            is_wait = True
            for line in result:
                if line.startswith("__WAIT__"):
                    wait_blocks = int(line.replace("__WAIT__", ""))
            console.print(f"[WAIT] [dim]#{state.clock_block:04d}[/] Advancing {wait_blocks} blocks...")

        before_idx = last_idx
        for _ in range(tick_count):
            _tick(state)
            
        last_idx = _print_new_logs(state, console, before_idx)
        
        if is_wait:
            console.print(f"[WAIT] [dim]#{state.clock_block:04d}[/] Done.")

        # Check for Phase Up (trigger screen immediately)
        if state.phase == GamePhase.ARCHITECT and not getattr(state, "_shown_architect_banner", False):
            console.print("\n"
                "  ╔══════════════════════════════════════════════╗\n"
                "  ║            PHASE UP: ARCHITECT               ║\n"
                "  ╠══════════════════════════════════════════════╣\n"
                "  ║  Capital target hit: $50,000.00              ║\n"
                "  ║  New capabilities unlocked:                  ║\n"
                "  ║    - audit    Scan protocols for vulns        ║\n"
                "  ║    - deploy protocol  Launch your own infra   ║\n"
                "  ║    - governance       Vote on proposals       ║\n"
                "  ║  New target: $500,000.00                     ║\n"
                "  ╚══════════════════════════════════════════════╝\n")
            state._shown_architect_banner = True

        if result:
            for line in result:
                if not line.startswith("__") and not line.startswith("[SYS] Autosaved"):
                    console.print(line)

    if not state.alive:
        nw = state.net_worth()
        console.print("\n"
            "  ╔══════════════════════════════════════════════╗\n"
            "  ║               TERMINAL: BURNED               ║\n"
            "  ╠══════════════════════════════════════════════╣\n"
            "  ║  Heat reached 100. Trace complete.           ║\n"
            "  ║  Your wallets are flagged. Funds frozen.     ║\n"
            "  ║                                              ║\n"
            "  ║  Final net worth:  $" + f"{nw:,.2f}".ljust(25) + "║\n"
            "  ║  Blocks survived:  #" + f"{state.clock_block:04d}".ljust(25) + "║\n"
            "  ║                                              ║\n"
            "  ║  Type `newgame` to start over.               ║\n"
            "  ╚══════════════════════════════════════════════╝\n")
        
        # Restricted prompt loop
        while not state.alive and state.running:
            try:
                raw = input("\n[DEAD]> ").strip()
                if not raw: continue
                if raw.lower() in ("quit", "q", "exit"): break
                if any(raw.lower().startswith(c) for c in ["newgame", "log", "save"]):
                    result = execute_command(state, raw)
                    if result and handle_special_result(result, state, console):
                        if state.alive: break # Re-entered game via newgame
                    if result:
                        for line in result:
                            if not line.startswith("__"): console.print(line)
                else:
                    console.print("[red]TERMINAL LOCKED.[/] Use `newgame` or `quit`.")
            except (EOFError, KeyboardInterrupt):
                break

    if state.won:
        console.print("\n[bold green]═══ YOU WIN ═══[/]")
        console.print("[dim]For now. The dark forest is patient.[/]")
    elif not state.alive and not state.running:
        console.print("\n[bold red]═══ GAME OVER ═══[/]")
        console.print("[dim]The chain remembers.[/]")
