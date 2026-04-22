"""Flavor text, system messages, and random event descriptions."""

from __future__ import annotations

import random

BOOT_MESSAGES = [
    "[dim]connecting to darkpool relay...[/]",
    "[dim]spoofing RPC endpoint...[/]",
    "[dim]loading mempool scanner...[/]",
    "[dim]calibrating gas oracle...[/]",
    "[dim]mounting encrypted keystore...[/]",
    "[dim]initializing chain indexer...[/]",
    "[dim]checking bridge status... [red]OFFLINE[/][/]",
    "[dim]syncing block headers...[/]",
]

SYSTEM_READY = """\
[bold green]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/]
[bold green]▓                                     ▓[/]
[bold green]▓     liquidate.exe  v0.1              ▓[/]
[bold green]▓     sudo_rug terminal interface      ▓[/]
[bold green]▓                                     ▓[/]
[bold green]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/]

[dim]You have one wallet. A dream. And plausible deniability.[/]
[dim]Type [cyan]help[/] to see available commands.[/]
[dim]Type [cyan]status[/] for your current situation.[/]
"""

TICK_FLAVOR = [
    "mempool quiet",
    "gas trending low",
    "whale wallet moved",
    "new token sniffed by MEV bots",
    "validators pruning stale txns",
    "governance proposal queued somewhere",
    "DEX aggregator indexed your pool",
    "CT anon posted a chart",
    "oracle heartbeat received",
    "bridge relayer lagging",
    "NFT floor collapsed on another chain",
    "stablecoin briefly depegged to $0.997",
    "VC wallet unlocked a tranche",
    "someone called your token a scam on reddit",
    "liquidity migrating to a competing DEX",
]

HEAT_FLAVOR_LOW = [
    "your wallet blends into the noise",
    "nothing interesting to see here",
    "on-chain activity unremarkable",
]

HEAT_FLAVOR_MED = [
    "a few accounts are watching your wallet",
    "your transaction pattern looks suspicious",
    "someone screenshotted your pool stats",
]

HEAT_FLAVOR_HIGH = [
    "etherscan tag pending for your address",
    "an anon is writing a thread about you",
    "your wallet is on 3 different watchlists",
    "a journalist just followed your deployer wallet",
]


def random_tick_flavor() -> str:
    """Get a random tick flavor message."""
    return random.choice(TICK_FLAVOR)


def random_heat_flavor(heat_level: float) -> str:
    """Get heat-appropriate flavor text."""
    if heat_level >= 60:
        return random.choice(HEAT_FLAVOR_HIGH)
    elif heat_level >= 30:
        return random.choice(HEAT_FLAVOR_MED)
    else:
        return random.choice(HEAT_FLAVOR_LOW)
