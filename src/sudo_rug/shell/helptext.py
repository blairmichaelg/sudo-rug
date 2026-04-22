"""Help text and command documentation."""

from __future__ import annotations

HELP_OVERVIEW = """\
[bold cyan]liquidate.exe[/] v0.1 — sudo_rug terminal

[bold]COMMANDS[/]
  [green]help[/]              Show this help (or help <command>)
  [green]status[/]            Show game state overview
  [green]wallet[/]            Show wallet balances
  [green]deploy meme[/]       Deploy a meme token
  [green]pool create[/]       Create a liquidity pool
  [green]trade buy[/]         Buy tokens with USD
  [green]trade sell[/]        Sell tokens for USD
  [green]bots run[/]          Hire bots to generate volume
  [green]liquidity pull[/]    Pull all liquidity (rug)
  [green]wait[/]              Skip blocks
  [green]logs[/]              Show recent log entries
  [green]quit[/]              Exit the game

Type [cyan]help <command>[/] for details on a specific command.
"""

HELP_DETAILS: dict[str, str] = {
    "deploy_meme": """\
[bold]deploy meme[/] — Deploy a new meme token

[bold]Usage:[/]
  deploy meme --ticker <TICKER> --supply <N>

[bold]Options:[/]
  --ticker    Token ticker symbol (2–8 chars, e.g. REKT)
  --supply    Total token supply (e.g. 1000000)

[bold]Effects:[/]
  - Creates the token and credits your wallet with full supply
  - Adds [yellow]+5 heat[/]
  - You can then create a pool to start trading

[bold]Example:[/]
  deploy meme --ticker REKT --supply 1000000
""",

    "pool_create": """\
[bold]pool create[/] — Create a constant-product liquidity pool

[bold]Usage:[/]
  pool create --token <TICKER> --base-amount <N> --token-amount <N>

[bold]Options:[/]
  --token         Token ticker to pair with USD
  --base-amount   USD to seed the pool with
  --token-amount  Tokens to seed the pool with

[bold]Effects:[/]
  - Creates a TICKER/USD pool
  - Deducts tokens and USD from your wallet
  - Initial price = base-amount / token-amount
  - Adds [yellow]+2 heat[/]

[bold]Example:[/]
  pool create --token REKT --base-amount 500 --token-amount 500000
""",

    "trade_buy": """\
[bold]trade buy[/] — Buy tokens with USD

[bold]Usage:[/]
  trade buy --market <TICKER>/USD --amount <N>

[bold]Options:[/]
  --market   Market pair (e.g. REKT/USD)
  --amount   USD to spend

[bold]Effects:[/]
  - Swaps USD for tokens via the AMM
  - 0.3% trade fee
  - Slippage depends on pool depth
  - Adds [yellow]+1 heat[/]

[bold]Example:[/]
  trade buy --market REKT/USD --amount 100
""",

    "trade_sell": """\
[bold]trade sell[/] — Sell tokens for USD

[bold]Usage:[/]
  trade sell --market <TICKER>/USD --amount <N>

[bold]Options:[/]
  --market   Market pair (e.g. REKT/USD)
  --amount   Token amount to sell

[bold]Effects:[/]
  - Swaps tokens for USD via the AMM
  - 0.3% trade fee
  - Slippage depends on pool depth
  - Adds [yellow]+1 heat[/]

[bold]Example:[/]
  trade sell --market REKT/USD --amount 50000
""",

    "bots_run": """\
[bold]bots run[/] — Hire bots to generate volume

[bold]Usage:[/]
  bots run --budget <N> --duration <N>

[bold]Options:[/]
  --budget     USD to allocate to bots
  --duration   Number of blocks bots will trade for

[bold]Effects:[/]
  - Deducts budget from your wallet
  - Bots make small buys each block, pumping price
  - You need at least one pool active
  - Adds [yellow]+3 heat[/]

[bold]Notes:[/]
  Bot activity is real — it uses the AMM, so prices actually move.
  Requires at least one active pool.

[bold]Example:[/]
  bots run --budget 200 --duration 10
""",

    "liquidity_pull": """\
[bold]liquidity pull[/] — Pull all liquidity from a pool (rug)

[bold]Usage:[/]
  liquidity pull --market <TICKER>/USD

[bold]Options:[/]
  --market   Market pair to drain

[bold]Effects:[/]
  - Removes ALL liquidity from the pool
  - Credits your wallet with the base + token reserves
  - Pool becomes empty (no more trading)
  - Adds [red]+30 heat[/] ⚠

[bold]Example:[/]
  liquidity pull --market REKT/USD
""",

    "wait": """\
[bold]wait[/] — Skip forward N blocks

[bold]Usage:[/]
  wait --blocks <N>

[bold]Options:[/]
  --blocks   Number of blocks to advance (default: 1)

[bold]Effects:[/]
  - Time passes, bots trade, heat decays
  - Events may trigger

[bold]Example:[/]
  wait --blocks 5
""",

    "status": """\
[bold]status[/] — Show current game state overview

Shows capital, holdings, heat, OpSec, net worth, active bots, and win/lose targets.
""",

    "wallet": """\
[bold]wallet[/] — Show wallet balances

Lists all currencies and their amounts.
""",

    "logs": """\
[bold]logs[/] — Show recent event log entries

Displays the last 20 log entries with block timestamps.
""",

    "help": """\
[bold]help[/] — Show help

[bold]Usage:[/]
  help            Show all commands
  help <command>  Show details for a command
""",

    "quit": """\
[bold]quit[/] — Exit the game

No save. No mercy.
""",
}
