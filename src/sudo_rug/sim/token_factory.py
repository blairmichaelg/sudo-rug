"""Token deployment logic."""

from __future__ import annotations

from sudo_rug.core.state import GameState, Token


def deploy_meme_token(
    state: GameState,
    ticker: str,
    supply: float,
) -> Token | str:
    """Deploy a new meme token. Returns Token or error string."""
    ticker = ticker.upper()

    if ticker in state.tokens:
        return f"Token {ticker} already exists"

    if ticker == "USD":
        return "Cannot use reserved ticker USD"

    if supply <= 0:
        return "Supply must be positive"

    if len(ticker) > 8:
        return "Ticker max 8 characters"

    if len(ticker) < 2:
        return "Ticker must be at least 2 characters"

    token = Token(
        ticker=ticker,
        total_supply=supply,
        deployer="player",
        block_created=state.clock_block,
    )

    state.tokens[ticker] = token
    state.wallet.credit(ticker, supply)

    return token
