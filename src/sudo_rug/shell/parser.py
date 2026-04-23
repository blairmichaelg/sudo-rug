"""Command parser — tokenize and route player input."""

from __future__ import annotations

import shlex
from typing import Any


def tokenize(raw: str) -> list[str]:
    """Split raw input into tokens, respecting quotes."""
    try:
        return shlex.split(raw.strip())
    except ValueError:
        return raw.strip().split()


def parse_args(tokens: list[str]) -> tuple[list[str], dict[str, str]]:
    """Parse tokens into positional args and --flag value pairs.

    Returns (positionals, flags).
    Example: ["deploy", "meme", "--ticker", "REKT", "--supply", "1000"]
    -> (["deploy", "meme"], {"ticker": "REKT", "supply": "1000"})
    """
    positionals: list[str] = []
    flags: dict[str, str] = {}

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("-"):
            key = token.lstrip("-").replace("-", "_")
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                flags[key] = tokens[i + 1]
                i += 2
            else:
                flags[key] = "true"
                i += 1
        else:
            positionals.append(token)
            i += 1

    return positionals, flags


def resolve_command(positionals: list[str]) -> tuple[str, list[str]]:
    """Resolve the command name from positionals.

    Supports compound commands like "deploy meme" or "trade buy".
    Returns (command_key, remaining_positionals).
    """
    if len(positionals) == 0:
        return "", []

    if len(positionals) >= 2:
        compound = f"{positionals[0]}_{positionals[1]}"
        return compound, positionals[2:]

    return positionals[0], positionals[1:]
