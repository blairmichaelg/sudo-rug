"""Main Textual application — wires UI, clock, and simulation together."""

from __future__ import annotations

import asyncio
import random

from textual.app import App, ComposeResult
from textual.widgets import Input

from sudo_rug.core.state import GameState
from sudo_rug.core.events import check_win_lose, check_heat_warnings, check_random_events
from sudo_rug.sim.bots import tick_bots
from sudo_rug.sim.heat import decay_heat
from sudo_rug.shell.commands import execute_command
from sudo_rug.content.messages import (
    BOOT_MESSAGES, SYSTEM_READY, random_tick_flavor, random_heat_flavor,
)
from sudo_rug.ui.screens import GameScreen
from sudo_rug.ui.log_view import GameLog
from sudo_rug.ui.status_panel import StatusPanel
from sudo_rug.ui.widgets import HeaderBar


class SudoRugApp(App):
    """The main game application."""

    TITLE = "liquidate.exe"
    CSS = """
    Screen {
        background: $surface;
    }
    """
    BINDINGS = [
        ("ctrl+c", "quit_game", "Quit"),
        ("ctrl+q", "quit_game", "Quit"),
    ]

    def __init__(self, state: GameState | None = None, **kwargs):
        super().__init__(**kwargs)
        self.state = state or GameState()
        self._clock_task: asyncio.Task | None = None
        self._boot_done = False
        self._waiting_blocks: int = 0
        self._last_log_idx: int = 0

        self._history_idx: int = -1
        self._cmd_history: list[str] = []

    def compose(self) -> ComposeResult:
        yield GameScreen()

    async def on_mount(self) -> None:
        """Start the boot sequence and clock."""
        # Run boot sequence
        asyncio.create_task(self._boot_sequence())

    async def _boot_sequence(self) -> None:
        """Animated boot sequence."""
        log = self.query_one("#game-log", GameLog)
        status = self.query_one("#status-panel", StatusPanel)
        header = self.query_one("#header", HeaderBar)

        header.refresh_block(0, True, False)

        # Boot messages with delays
        for msg in BOOT_MESSAGES:
            log.write(msg)
            if not getattr(self, "_skip_boot_delays", False):
                await asyncio.sleep(0.15)

        if not getattr(self, "_skip_boot_delays", False):
            await asyncio.sleep(0.3)
        log.write(SYSTEM_READY)

        self.state.add_log("System initialized. Welcome to the dark forest.", style="green")
        self.state.add_log(
            f"Starting capital: ${self.state.config.start_capital:,.2f}. "
            f"Target: ${self.state.config.win_target:,.0f}.",
        )

        status.refresh_state(self.state)
        self._boot_done = True
        self._skip_boot_delays = False

        # Start the clock
        self._clock_task = asyncio.create_task(self._run_clock())

    async def _run_clock(self) -> None:
        """Main simulation clock."""
        while self.state.running and self.state.alive:
            await asyncio.sleep(self.state.config.tick_interval)
            if not self.state.running or not self.state.alive:
                break
            await self._tick()

    async def _tick(self) -> None:
        """Process one block tick."""
        self.state.clock_block += 1
        block = self.state.clock_block

        # Autosave every 50 blocks
        if block > 0 and block % 50 == 0:
            import json
            from pathlib import Path
            save_dir = Path.home() / ".sudo_rug"
            save_dir.mkdir(parents=True, exist_ok=True)
            with open(save_dir / "save.json", "w") as f:
                json.dump(self.state.to_dict(), f)
            self.state.add_log("[dim]Autosaved.[/]")

        log = self.query_one("#game-log", GameLog)
        status = self.query_one("#status-panel", StatusPanel)
        header = self.query_one("#header", HeaderBar)

        # 1. Decay heat
        decay_heat(self.state)

        # 2. Tick bots
        bot_messages = tick_bots(self.state)
        for msg in bot_messages:
            self.state.add_log(msg)

        # 2.5 Random events
        rand_events = check_random_events(self.state)
        for r in rand_events:
            self.state.add_log(r)

        # 3. Random ambient flavor (30% chance)
        if random.random() < 0.30:
            flavor = random_tick_flavor()
            self.state.add_log(f"[dim]{flavor}[/]")

        # 4. Heat-based ambient (20% chance when heat > 10)
        if self.state.heat.level > 10 and random.random() < 0.20:
            hf = random_heat_flavor(self.state.heat.level)
            self.state.add_log(f"[dim italic]{hf}[/]")

        # 5. Check heat warnings
        warnings = check_heat_warnings(self.state)
        for w in warnings:
            self.state.add_log(w, style="bold yellow")

        # 6. Check win/lose
        result = check_win_lose(self.state)

        # 7. Update UI
        # Flush new log entries to the widget
        self._flush_logs(log)
        status.refresh_state(self.state)
        header.refresh_block(block, self.state.alive, self.state.won)

        # 8. Handle waiting
        if self._waiting_blocks > 0:
            self._waiting_blocks -= 1

        # 9. Handle game end
        if result is not None:
            self._flush_logs(log)
            if not self.state.alive:
                log.write("\n[bold red]═══ GAME OVER ═══[/]")
                log.write("[dim]The chain remembers. You didn't move fast enough.[/]")
            elif self.state.won:
                log.write("\n[bold green]═══ YOU WIN ═══[/]")
                log.write("[dim]For now. The dark forest is patient.[/]")

    def _flush_logs(self, log: GameLog) -> None:
        """Write any pending log entries to the log widget."""
        entries = self.state.log[self._last_log_idx:]
        for entry in entries:
            log.write_game(entry.block, entry.message, entry.style)
        self._last_log_idx = len(self.state.log)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input."""
        raw = event.value.strip()
        event.input.value = ""

        if not raw:
            return

        if not self._cmd_history or self._cmd_history[0] != raw:
            self._cmd_history.insert(0, raw)
        if len(self._cmd_history) > 50:
            self._cmd_history.pop()
        self._history_idx = -1

        if not self._boot_done:
            return

        if not self.state.alive or self.state.won:
            if raw.lower() in ("quit", "exit", "q"):
                self.exit()
            return

        log = self.query_one("#game-log", GameLog)
        status = self.query_one("#status-panel", StatusPanel)

        # Echo the command
        log.write(f"\n[bold cyan]> {raw}[/]")

        # Execute
        from sudo_rug.core.state import GameState
        output = execute_command(self.state, raw)

        # Handle wait command
        if output and output[0].startswith("__WAIT__"):
            blocks = int(output[0].replace("__WAIT__", ""))
            self._waiting_blocks = blocks
            log.write(f"[dim]Waiting {blocks} blocks...[/]")
            # Fast-forward ticks
            for _ in range(blocks):
                await self._tick()
                await asyncio.sleep(0.02)
            log.write(f"[dim]...{blocks} blocks passed.[/]")
        elif output and output[0] == "__NEWGAME__":
            from pathlib import Path
            save_path = Path.home() / ".sudo_rug" / "save.json"
            if save_path.exists():
                save_path.unlink()
            if self._clock_task:
                self._clock_task.cancel()
            self.state.running = False
            self.state = GameState()
            self._last_log_idx = 0
            log.clear()
            self._skip_boot_delays = True
            self.state.add_log("[dim]Starting fresh run.[/]")
            asyncio.create_task(self._boot_sequence())
        elif output and output[0].startswith("__LOAD_JSON__"):
            import json
            parts = output[0].split("\n", 1)
            try:
                data = json.loads(parts[1])
                new_state = GameState.from_dict(data)
                
                if self._clock_task:
                    self._clock_task.cancel()
                self.state.running = False
                self.state = new_state
                self._last_log_idx = len(self.state.log)
                
                log.write(f"[green]✓ loaded from Block #{self.state.clock_block}.[/]")
                log.write(f"  Capital: ${self.state.wallet.get('USD'):,.2f}")
                log.write(f"  Heat: {self.state.heat.level:.1f}")
                log.write(f"  OpSec Tier: {self.state.opsec_tier}")
                
                status.refresh_state(self.state)
                self.query_one("#header", HeaderBar).refresh_block(self.state.clock_block, True, False)
                
                self.state.running = True
                self._clock_task = asyncio.create_task(self._run_clock())
            except Exception as e:
                log.write(f"[red]Error parsing save:[/] {e}")
        else:
            # Normal output
            for line in output:
                log.write(line)

        # Flush logs and refresh status
        self._flush_logs(log)
        status.refresh_state(self.state)
        header = self.query_one("#header", HeaderBar)
        header.refresh_block(
            self.state.clock_block, self.state.alive, self.state.won
        )

    async def on_key(self, event) -> None:
        """Handle command history up/down arrows."""
        if not self._cmd_history:
            return
            
        inp = self.query_one("Input", Input)
        if event.key == "up":
            if self._history_idx < len(self._cmd_history) - 1:
                self._history_idx += 1
            inp.value = self._cmd_history[self._history_idx]
            inp.cursor_position = len(inp.value)
        elif event.key == "down":
            if self._history_idx > 0:
                self._history_idx -= 1
                inp.value = self._cmd_history[self._history_idx]
                inp.cursor_position = len(inp.value)
            elif self._history_idx == 0:
                self._history_idx = -1
                inp.value = ""

    def action_quit_game(self) -> None:
        """Quit the game."""
        self.state.running = False
        self.exit()
