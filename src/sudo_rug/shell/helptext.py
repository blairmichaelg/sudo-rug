"""Command help texts."""

HELP_OVERVIEW = """sudo-rug v1 — dark-forest terminal sim

INFO
  help [cmd]              Show commands or detail for a command.
  status (.)              Block, net worth, heat, opsec.
  log (/)                 Last 20 system events.
  risk (!)                Heat breakdown and consequences.

ACCOUNTS
  wallet ($)              Balances and exposures.
  pos                     Pool exposures as % of net worth.

TOKENS & POOLS
  launch -t X -s N        Deploy a meme token.
  seed X/USD -u N -n N    Seed a liquidity pool.
  rug X/USD               Pull liquidity (exit scam).

TRADING
  buy -m X/USD -a N       Buy tokens from a pool.
  sell -m X/USD -a N      Sell tokens into a pool.

BOTS
  snipe -b N -d N         Hire hype bots on a pool.
  bots                    Show active bots.

TIME
  wait N (w)              Advance N blocks.

META
  save / load / newgame / quit

Type `help <cmd>` for flags and an example."""

HELP_DETAILS = {
    "status": "status (.)\n\nShow block, net worth, heat, opsec at a glance.\nExample: .\n[dim]The chain is public, but your identity is not.[/]",
    "wallet": "wallet ($)\n\nShow USD and token balances.\nExample: $\n[dim]Your bags, transparent for all to see.[/]",
    "log": "log (/)\n\nShow the last 20 system events.\nExample: /\n[dim]The dark forest chatters.[/]",
    "risk": "risk (!)\n\nShow current heat, opsec tiers, and consequences.\nExample: !\n[dim]Assess how close they are to finding you.[/]",
    "pos": "pos\n\nShow all pool exposures as a % of your net worth.\nExample: pos\n[dim]Know your systemic risk.[/]",
    "launch": "launch\n\nDeploy a meme token.\nFlags: -t / --ticker <str>, -s / --supply <float>\nExample: launch -t REKT -s 1000000\n[dim]Create a new shitcoin out of thin air.[/]",
    "seed": "seed\n\nSeed a liquidity pool.\nFlags: -u / --base-amount <float>, -n / --token-amount <float>\nExample: seed REKT/USD -u 500 -n 500000\n[dim]Provide liquidity to the AMM so plebs can buy.[/]",
    "rug": "rug\n\nPull liquidity (exit scam).\nExample: rug REKT/USD\n[dim]Yank the liquidity and run. High heat generation.[/]",
    "buy": "buy (b)\n\nBuy tokens from a pool.\nFlags: -m / --market <str>, -a / --amount <float (USD)>\nExample: buy -m REKT/USD -a 100\n[dim]Ape in with USD.[/]",
    "sell": "sell (s)\n\nSell tokens into a pool.\nFlags: -m / --market <str>, -a / --amount <float (tokens)>\nExample: sell -m REKT/USD -a 5000\n[dim]Dump your bags on the market.[/]",
    "snipe": "snipe\n\nDeploy hype bots on a pool.\nFlags: -b / --budget <float>, -d / --duration <int blocks>, [-m / --market <str>]\nExample: snipe -b 200 -d 10\n[dim]Pay for CT volume and fake hype to bait buyers.[/]",
    "bots": "bots\n\nShow active bots and budgets.\nExample: bots\n[dim]Track your deployed mercenaries.[/]",
    "wait": "wait (w)\n\nAdvance N blocks.\nExample: w 10\n[dim]Let the simulation advance while you plan your next move.[/]",
    "save": "save\n\nSave your progress.\nExample: save\n[dim]Snapshot your wallet state offline.[/]",
    "load": "load\n\nLoad progress.\nExample: load\n[dim]Restore your snapshot.[/]",
    "newgame": "newgame\n\nStart a new run.\nExample: newgame confirm\n[dim]Burn it all down and start over.[/]",
    "quit": "quit\n\nDisconnect from the simulation.\nExample: quit\n[dim]Go dark.[/]"
}
