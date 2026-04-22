"""Command handlers — route parsed input to game logic."""

from __future__ import annotations

from typing import Callable, Any

from sudo_rug.core.state import GameState, Pool
from sudo_rug.core.enums import ActionType
from sudo_rug.sim.token_factory import deploy_meme_token
from sudo_rug.sim.market import execute_buy, execute_sell, pull_liquidity
from sudo_rug.sim.bots import create_bot_job
from sudo_rug.sim.heat import add_heat, get_heat_bar, check_heat_lockdown
from sudo_rug.sim.opsec import get_opsec_rating
from sudo_rug.shell.helptext import HELP_OVERVIEW, HELP_DETAILS


# Type for command handlers: (state, positionals, flags) -> list of output lines
CommandHandler = Callable[[GameState, list[str], dict[str, str]], list[str]]


def cmd_help(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Show help."""
    if pos:
        key = pos[0]
        # Try compound
        if len(pos) >= 2:
            compound = f"{pos[0]}_{pos[1]}"
            if compound in HELP_DETAILS:
                return [HELP_DETAILS[compound]]
        if key in HELP_DETAILS:
            return [HELP_DETAILS[key]]
        return [f"[red]No help found for '{key}'[/]"]
    return [HELP_OVERVIEW]


def cmd_status(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Show game status."""
    nw = state.net_worth()
    tier_info = ""
    if state.opsec_tier == 0:
        tier_info = " (Tier 1: $500)"
    elif state.opsec_tier == 1:
        tier_info = " (Tier 2: $2,000)"
    elif state.opsec_tier == 2:
        tier_info = " (Tier 3: $8,000)"
    else:
        tier_info = " (MAX)"

    lines = [
        f"[bold cyan]═══ STATUS ═══[/]",
        f"  Block:     [white]#{state.clock_block}[/]",
        f"  Phase:     [magenta]{state.phase.name}[/]",
        f"  Net Worth: [{'green' if nw >= state.config.win_target * 0.5 else 'white'}]${nw:,.2f}[/]"
        f"  (target: ${state.config.win_target:,.0f})",
        f"  Heat:      {get_heat_bar(state.heat.level)}",
        f"  OpSec:     {get_opsec_rating(state)}{tier_info}",
        f"  USD:       [green]${state.wallet.get('USD'):,.2f}[/]",
    ]

    # Token holdings
    for ticker in state.tokens:
        held = state.wallet.get(ticker)
        pool_key = f"{ticker}/USD"
        if pool_key in state.pools:
            price = state.pools[pool_key].price
            value = held * price
            lines.append(
                f"  {ticker}:    {held:,.2f} "
                f"(${price:.6f}/ea = ${value:,.2f})"
            )
        else:
            lines.append(f"  {ticker}:    {held:,.2f} (no pool)")

    # Active pools
    if state.pools:
        lines.append(f"\n[bold]Pools:[/]")
        for key, pool in state.pools.items():
            if pool.reserve_base > 0:
                lines.append(
                    f"  {key}: {pool.reserve_token:,.2f} / "
                    f"${pool.reserve_base:,.2f} "
                    f"(price: ${pool.price:.6f})"
                )
            else:
                lines.append(f"  {key}: [dim]drained[/]")

    # Active bots
    if state.bots:
        lines.append(f"\n[bold]Active Bots:[/] {len(state.bots)}")
        for i, bot in enumerate(state.bots):
            lines.append(
                f"  bot#{i}: {bot.market} — "
                f"${bot.budget_remaining:,.2f} remaining, "
                f"{bot.blocks_remaining} blocks left"
            )

    return lines


def cmd_wallet(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Show wallet balances."""
    lines = ["[bold cyan]═══ WALLET ═══[/]"]
    for currency, amount in sorted(state.wallet.balances.items()):
        if amount > 0 or currency == "USD":
            if currency == "USD":
                lines.append(f"  [green]${amount:,.2f}[/] USD")
            else:
                lines.append(f"  [white]{amount:,.2f}[/] {currency}")
    return lines


def cmd_deploy_meme(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Deploy a meme token."""
    ticker = flags.get("ticker")
    supply_str = flags.get("supply")

    if not ticker:
        return ["[red]Missing --ticker[/]. Usage: deploy meme --ticker REKT --supply 1000000"]
    if not supply_str:
        return ["[red]Missing --supply[/]. Usage: deploy meme --ticker REKT --supply 1000000"]

    try:
        supply = float(supply_str)
    except ValueError:
        return [f"[red]Invalid supply: {supply_str}[/]"]

    allowed, penalty, lock_msg = check_heat_lockdown(state, ActionType.DEPLOY_TOKEN)
    if not allowed:
        return [lock_msg]

    result = deploy_meme_token(state, ticker, supply)
    if isinstance(result, str):
        return [f"[red]{result}[/]"]

    heat_added = add_heat(state, ActionType.DEPLOY_TOKEN)
    if penalty > 0:
        state.heat.level += penalty
        state.heat.history[-1] = (state.clock_block, state.heat.level)
        heat_added += penalty

    state.add_log(
        f"TOKEN DEPLOYED: ${result.ticker} — supply: {result.total_supply:,.0f}",
        style="bold magenta"
    )
    res_lines = [
        f"[green]✓[/] Deployed [bold]{result.ticker}[/] — supply: {result.total_supply:,.0f}",
        f"  Credited to wallet. Heat +{heat_added:.1f}",
    ]
    if penalty > 0:
        res_lines.append(f"  {lock_msg}")
    res_lines.append(f"  Next: create a pool with [cyan]pool create --token {result.ticker} --base-amount <N> --token-amount <N>[/]")
    return res_lines


def cmd_pool_create(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Create a liquidity pool."""
    ticker = flags.get("token", "").upper()
    base_str = flags.get("base_amount")
    token_str = flags.get("token_amount")

    if not ticker:
        return ["[red]Missing --token[/]. Usage: pool create --token REKT --base-amount 500 --token-amount 500000"]
    if not base_str:
        return ["[red]Missing --base-amount[/]"]
    if not token_str:
        return ["[red]Missing --token-amount[/]"]

    try:
        base_amount = float(base_str)
        token_amount = float(token_str)
    except ValueError:
        return ["[red]Invalid amount[/]"]

    if ticker not in state.tokens:
        return [f"[red]Token {ticker} does not exist. Deploy it first.[/]"]

    market_key = f"{ticker}/USD"
    if market_key in state.pools:
        return [f"[red]Pool {market_key} already exists[/]"]

    if not state.wallet.debit("USD", base_amount):
        return [f"[red]Insufficient USD (have ${state.wallet.get('USD'):,.2f}, need ${base_amount:,.2f})[/]"]

    if not state.wallet.debit(ticker, token_amount):
        state.wallet.credit("USD", base_amount)  # refund
        return [f"[red]Insufficient {ticker} (have {state.wallet.get(ticker):,.2f}, need {token_amount:,.2f})[/]"]

    allowed, penalty, lock_msg = check_heat_lockdown(state, ActionType.CREATE_POOL)
    if not allowed:
        state.wallet.credit("USD", base_amount)
        state.wallet.credit(ticker, token_amount)
        return [lock_msg]

    pool = Pool(
        token=ticker,
        base="USD",
        reserve_token=token_amount,
        reserve_base=base_amount,
    )
    state.pools[market_key] = pool

    heat_added = add_heat(state, ActionType.CREATE_POOL)
    if penalty > 0:
        state.heat.level += penalty
        state.heat.history[-1] = (state.clock_block, state.heat.level)
        heat_added += penalty

    initial_price = pool.price
    state.add_log(
        f"POOL CREATED: {market_key} — "
        f"${base_amount:,.2f} / {token_amount:,.0f} {ticker} "
        f"(price: ${initial_price:.6f})",
        style="bold blue"
    )

    res = [
        f"[green]✓[/] Pool [bold]{market_key}[/] created",
        f"  Seeded: ${base_amount:,.2f} + {token_amount:,.0f} {ticker}",
        f"  Initial price: [cyan]${initial_price:.6f}[/]",
        f"  Heat +{heat_added:.1f}",
    ]
    if penalty > 0:
        res.append(f"  {lock_msg}")
    return res


def cmd_trade_buy(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Buy tokens."""
    market = flags.get("market", "").upper()
    amount_str = flags.get("amount")

    if not market:
        return ["[red]Missing --market[/]. Usage: trade buy --market REKT/USD --amount 100"]
    if not amount_str:
        return ["[red]Missing --amount[/]"]

    try:
        amount = float(amount_str)
    except ValueError:
        return [f"[red]Invalid amount: {amount_str}[/]"]

    allowed, penalty, lock_msg = check_heat_lockdown(state, ActionType.TRADE_BUY)
    if not allowed:
        return [lock_msg]

    result = execute_buy(state, market, amount)
    if isinstance(result, str):
        return [f"[red]{result}[/]"]

    heat_added = add_heat(state, ActionType.TRADE_BUY)
    if penalty > 0:
        state.heat.level += penalty
        state.heat.history[-1] = (state.clock_block, state.heat.level)
        heat_added += penalty

    state.add_log(
        f"BUY: {result.amount_out:.2f} tokens on {market} "
        f"for ${amount:.2f} (price: ${result.price_before:.6f} [green]▲[/] ${result.price_after:.6f})",
    )

    res = [
        f"[green]✓[/] Bought [bold]{result.amount_out:,.2f}[/] tokens",
        f"  Spent: ${amount:,.2f}",
        f"  Price: ${result.price_before:.6f} [green]▲[/] ${result.price_after:.6f}",
        f"  Fee: ${result.fee_paid:.4f}",
        f"  Heat +{heat_added:.1f}",
    ]
    if penalty > 0:
        res.append(f"  {lock_msg}")
    return res


def cmd_trade_sell(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Sell tokens."""
    market = flags.get("market", "").upper()
    amount_str = flags.get("amount")

    if not market:
        return ["[red]Missing --market[/]. Usage: trade sell --market REKT/USD --amount 50000"]
    if not amount_str:
        return ["[red]Missing --amount[/]"]

    try:
        amount = float(amount_str)
    except ValueError:
        return [f"[red]Invalid amount: {amount_str}[/]"]

    allowed, penalty, lock_msg = check_heat_lockdown(state, ActionType.TRADE_SELL)
    if not allowed:
        return [lock_msg]

    result = execute_sell(state, market, amount)
    if isinstance(result, str):
        return [f"[red]{result}[/]"]

    heat_added = add_heat(state, ActionType.TRADE_SELL)
    if penalty > 0:
        state.heat.level += penalty
        state.heat.history[-1] = (state.clock_block, state.heat.level)
        heat_added += penalty

    state.add_log(
        f"SELL: {amount:.2f} tokens on {market} "
        f"for ${result.amount_out:.2f} (price: ${result.price_before:.6f} [red]▼[/] ${result.price_after:.6f})",
    )

    res = [
        f"[green]✓[/] Sold [bold]{amount:,.2f}[/] tokens",
        f"  Received: [green]${result.amount_out:,.2f}[/]",
        f"  Price: ${result.price_before:.6f} [red]▼[/] ${result.price_after:.6f}",
        f"  Fee: ${result.fee_paid:.4f}",
        f"  Heat +{heat_added:.1f}",
    ]
    if penalty > 0:
        res.append(f"  {lock_msg}")
    return res


def cmd_bots_run(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Hire bots."""
    budget_str = flags.get("budget")
    duration_str = flags.get("duration")

    if not budget_str:
        return ["[red]Missing --budget[/]. Usage: bots run --budget 200 --duration 10"]
    if not duration_str:
        return ["[red]Missing --duration[/]"]

    try:
        budget = float(budget_str)
        duration = int(duration_str)
    except ValueError:
        return ["[red]Invalid budget or duration[/]"]

    market_flag = flags.get("market", "").upper()

    allowed, penalty, lock_msg = check_heat_lockdown(state, ActionType.RUN_BOTS)
    if not allowed:
        return [lock_msg]

    if not market_flag:
        # Find the first active pool to target
        active_pools = [k for k, p in state.pools.items() if p.reserve_base > 0]
        if not active_pools:
            return ["[red]No active pools. Create a pool first.[/]"]
        market_key = active_pools[0]
    else:
        market_key = market_flag
        if market_key not in state.pools or state.pools[market_key].reserve_base <= 0:
            return [f"[red]Market {market_key} not found or drained.[/]"]

    result = create_bot_job(state, budget, duration, market_key)
    if isinstance(result, str):
        return [f"[red]{result}[/]"]

    heat_added = add_heat(state, ActionType.RUN_BOTS)
    state.add_log(
        f"BOTS HIRED: ${budget:.2f} budget, {duration} blocks on {market_key}",
        style="bold yellow"
    )

    return [
        f"[green]✓[/] Bots deployed",
        f"  Market: [cyan]{market_key}[/] {'(auto-selected)' if not market_flag else ''}",
        f"  Budget: ${budget:,.2f} over {duration} blocks",
        f"  (~${result.spend_per_block:,.2f}/block)",
        f"  Heat +{heat_added:.1f}",
    ]


def cmd_liquidity_pull(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Pull liquidity (rug)."""
    market = flags.get("market", "").upper()

    if not market:
        return ["[red]Missing --market[/]. Usage: liquidity pull --market REKT/USD"]

    allowed, penalty, lock_msg = check_heat_lockdown(state, ActionType.PULL_LIQUIDITY)
    if not allowed:
        return [lock_msg]

    result = pull_liquidity(state, market)
    if isinstance(result, str):
        return [f"[red]{result}[/]"]

    base_out, token_out = result
    heat_added = add_heat(state, ActionType.PULL_LIQUIDITY)
    if penalty > 0:
        state.heat.level += penalty
        state.heat.history[-1] = (state.clock_block, state.heat.level)
        heat_added += penalty

    state.add_log(
        f"⚠ LIQUIDITY PULLED: {market} — "
        f"${base_out:,.2f} + {token_out:,.0f} tokens recovered. "
        f"Heat +{heat_added:.1f}",
        style="bold red"
    )

    return [
        f"[bold red]☠ RUG EXECUTED[/] on [bold]{market}[/]",
        f"  Recovered: [green]${base_out:,.2f}[/] USD + {token_out:,.0f} tokens",
        f"  Pool is now [red]DRAINED[/]",
        f"  Heat [red]+{heat_added:.1f}[/] ⚠",
    ]


def cmd_wait(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Wait N blocks. Actual ticking handled by the app."""
    blocks_str = flags.get("blocks", "1")
    try:
        blocks = int(blocks_str)
    except ValueError:
        return ["[red]Invalid block count[/]"]

    if blocks < 1:
        return ["[red]Must wait at least 1 block[/]"]
    if blocks > 50:
        return ["[red]Max 50 blocks at a time[/]"]

    # Return special marker for the app to handle
    return [f"__WAIT__{blocks}"]


def cmd_logs(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Show recent log entries."""
    entries = state.log[-20:]
    if not entries:
        return ["[dim]No log entries yet.[/]"]

    lines = ["[bold cyan]═══ RECENT LOGS ═══[/]"]
    for entry in entries:
        if entry.style:
            lines.append(f"  [dim]#{entry.block:>4}[/] [{entry.style}]{entry.message}[/]")
        else:
            lines.append(f"  [dim]#{entry.block:>4}[/] {entry.message}")
    return lines


def cmd_quit(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Quit the game."""
    state.running = False
    return ["[dim]Disconnecting...[/]"]


def cmd_opsec_upgrade(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Upgrade OpSec."""
    from sudo_rug.sim.heat import check_heat_lockdown
    allowed, _, lock_msg = check_heat_lockdown(state, ActionType.OPSEC_UPGRADE)
    if not allowed:
        return [lock_msg]

    tier_str = flags.get("tier")
    if not tier_str:
        return ["[red]Missing --tier[/]. Usage: opsec upgrade --tier <1|2|3>"]
    
    try:
        target_tier = int(tier_str)
    except ValueError:
        return ["[red]Tier must be 1, 2, or 3.[/]"]
        
    if target_tier <= state.opsec_tier:
        return [f"[red]You already have OpSec tier {state.opsec_tier}.[/]"]
    if target_tier != state.opsec_tier + 1:
        return [f"[red]Must purchase tiers in order. Current tier {state.opsec_tier}. Next is {state.opsec_tier + 1}.[/]"]
        
    costs = {1: 500.0, 2: 2000.0, 3: 8000.0}
    if target_tier not in costs:
        return ["[red]Unknown tier. Tiers are 1, 2, 3.[/]"]
        
    cost = costs[target_tier]
    if not state.wallet.debit("USD", cost):
        return [f"[red]Insufficient USD (have ${state.wallet.get('USD'):,.2f}, need ${cost:,.2f})[/]"]
        
    state.opsec_tier = target_tier
    if target_tier == 1:
        state.opsec = 0.20
        state.config.heat_decay_per_block += 0.1
        desc = "burner wallet"
    elif target_tier == 2:
        state.opsec = 0.40
        state.config.heat_decay_per_block += 0.2
        desc = "VPN + mixer"
    else:
        state.opsec = 0.65
        state.config.heat_decay_per_block += 0.3
        desc = "full dark stack"
        
    return [
        f"[green]✓[/] OpSec upgraded to Tier {target_tier}: {desc}",
        f"  Cost: ${cost:,.2f}",
        f"  Protection: {state.opsec*100:.0f}%",
        f"  Heat Decay: {state.config.heat_decay_per_block:.1f}/block",
    ]


def cmd_save(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Save the game."""
    import json
    from pathlib import Path
    save_dir = Path.home() / ".sudo_rug"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / "save.json"
    
    with open(save_path, "w") as f:
        json.dump(state.to_dict(), f, indent=2)
        
    return [f"[green]✓[/] Game saved to ~/.sudo_rug/save.json (Block #{state.clock_block})"]


def cmd_load(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Load the game."""
    import json
    from pathlib import Path
    save_path = Path.home() / ".sudo_rug" / "save.json"
    
    if not save_path.exists():
        return ["[red]No save file found at ~/.sudo_rug/save.json[/]"]
        
    try:
        with open(save_path, "r") as f:
            data = json.load(f)
        return [f"__LOAD_JSON__\n{json.dumps(data)}"]
    except Exception as e:
        return [f"[red]Error loading save:[/] {e}"]


def cmd_newgame(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
    """Start a new game."""
    if pos and pos[0] == "confirm":
        return ["__NEWGAME__"]
    return ["Current run will be lost. Type [cyan]newgame confirm[/] to start fresh."]


# ─── Command Registry ────────────────────────────────────────────────────────

COMMANDS: dict[str, CommandHandler] = {
    "help": cmd_help,
    "status": cmd_status,
    "wallet": cmd_wallet,
    "deploy_meme": cmd_deploy_meme,
    "pool_create": cmd_pool_create,
    "trade_buy": cmd_trade_buy,
    "trade_sell": cmd_trade_sell,
    "bots_run": cmd_bots_run,
    "liquidity_pull": cmd_liquidity_pull,
    "wait": cmd_wait,
    "logs": cmd_logs,
    "opsec_upgrade": cmd_opsec_upgrade,
    "save": cmd_save,
    "load": cmd_load,
    "newgame": cmd_newgame,
    "quit": cmd_quit,
}


def execute_command(state: GameState, raw_input: str) -> list[str]:
    """Parse and execute a command. Returns output lines."""
    from sudo_rug.shell.parser import tokenize, parse_args, resolve_command

    tokens = tokenize(raw_input)
    if not tokens:
        return []

    positionals, flags = parse_args(tokens)
    command_key, remaining = resolve_command(positionals)

    handler = COMMANDS.get(command_key)
    if handler is None:
        # Try single-word fallback
        if positionals:
            handler = COMMANDS.get(positionals[0])
            remaining = positionals[1:]
    if handler is None:
        suggestions = [k.replace("_", " ") for k in COMMANDS if k.startswith(command_key[:2])]
        hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
        return [f"[red]Unknown command: {raw_input}[/]{hint}", "Type [cyan]help[/] for available commands."]

    return handler(state, remaining, flags)
