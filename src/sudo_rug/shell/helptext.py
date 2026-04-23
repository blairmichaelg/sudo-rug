"""Command help texts."""

HELP_OVERVIEW = """sudo-rug v1 — dark-forest terminal sim

INFO
  help [cmd]     Show commands or detail for a command.
  status (s)     Block, net worth, heat, opsec at a glance.
  log (l)        Last 20 system events.
  risk (r)       Current heat/opsec breakdown and consequences.

ACCOUNTS
  wallet (w)     Balances and exposures.
  positions      All pool exposures as % of net worth.

TOKENS & POOLS
  token deploy   Launch a new meme token.
  pool create    Seed a token/USD pool.
  pool drain     Pull your liquidity (rug).

TRADING
  trade buy      Buy tokens from a pool.
  trade sell     Sell tokens into a pool.

BOTS
  bots hire      Deploy hype bots on a pool.
  bots list      Show active bots and budgets.

TIME
  wait N         Advance N blocks.

META
  save / load / newgame / quit

Type `help <cmd>` for flags and an example."""

HELP_DETAILS = {
    "status": "status\n\nShow block, net worth, heat, opsec at a glance.\nExample: status\n[dim]The chain is public, but your identity is not.[/]",
    "s": "Alias for status.",
    "wallet": "wallet\n\nShow USD and token balances.\nExample: wallet\n[dim]Your bags, transparent for all to see.[/]",
    "w": "Alias for wallet.",
    "log": "log\n\nShow the last 20 system events.\nExample: log\n[dim]The dark forest chatters.[/]",
    "l": "Alias for log.",
    "risk": "risk\n\nShow current heat, opsec tiers, and consequences.\nExample: risk\n[dim]Assess how close they are to finding you.[/]",
    "r": "Alias for risk.",
    "positions": "positions\n\nShow all pool exposures as a % of your net worth.\nExample: positions\n[dim]Know your systemic risk.[/]",
    "pos": "Alias for positions.",
    "token_deploy": "token deploy\n\nLaunch a new meme token.\nFlags: --ticker <str> --supply <float>\nExample: token deploy --ticker REKT --supply 1000000\n[dim]Create a new shitcoin out of thin air.[/]",
    "deploy": "Alias for token deploy.",
    "pool_create": "pool create\n\nSeed a token/USD pool.\nFlags: --token <str> --base-amount <float> --token-amount <float>\nExample: pool create --token REKT --base-amount 500 --token-amount 500000\n[dim]Provide liquidity to the AMM so plebs can buy.[/]",
    "pool_drain": "pool drain\n\nPull your liquidity (rug).\nFlags: --market <str>\nExample: pool drain --market REKT/USD\n[dim]Yank the liquidity and run. High heat generation.[/]",
    "rug": "Alias for pool drain.",
    "trade_buy": "trade buy\n\nBuy tokens from a pool.\nFlags: --market <str> --amount <float (USD)>\nExample: trade buy --market REKT/USD --amount 100\n[dim]Ape in with USD.[/]",
    "buy": "Alias for trade buy.",
    "trade_sell": "trade sell\n\nSell tokens into a pool.\nFlags: --market <str> --amount <float (tokens)>\nExample: trade sell --market REKT/USD --amount 5000\n[dim]Dump your bags on the market.[/]",
    "sell": "Alias for trade sell.",
    "bots_hire": "bots hire\n\nDeploy hype bots on a pool.\nFlags: --budget <float> --duration <int blocks> [--market <str>]\nExample: bots hire --budget 200 --duration 10\n[dim]Pay for CT volume and fake hype to bait buyers.[/]",
    "bots_list": "bots list\n\nShow active bots and budgets.\nExample: bots list\n[dim]Track your deployed mercenaries.[/]",
    "wait": "wait N\n\nAdvance N blocks.\nExample: wait 10\n[dim]Let the simulation advance while you plan your next move.[/]",
    "save": "save\n\nSave your progress to ~/.sudo_rug/save.json.\nExample: save\n[dim]Snapshot your wallet state offline.[/]",
    "load": "load\n\nLoad progress from ~/.sudo_rug/save.json.\nExample: load\n[dim]Restore your snapshot.[/]",
    "newgame": "newgame\n\nStart a new run.\nExample: newgame confirm\n[dim]Burn it all down and start over.[/]",
    "quit": "quit\n\nDisconnect from the simulation.\nExample: quit\n[dim]Go dark.[/]"
}
