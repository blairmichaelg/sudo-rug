"""Tests for command parsing and execution."""

import pytest
from sudo_rug.shell.parser import tokenize, parse_args, resolve_command
from sudo_rug.shell.commands import execute_command
from sudo_rug.core.state import GameState, GameConfig


# ─── Parser Tests ─────────────────────────────────────────────────────────────


class TestTokenize:
    def test_simple(self):
        assert tokenize("help") == ["help"]

    def test_compound(self):
        assert tokenize("deploy meme --ticker REKT") == [
            "deploy", "meme", "--ticker", "REKT"
        ]

    def test_whitespace(self):
        assert tokenize("  help  ") == ["help"]

    def test_empty(self):
        assert tokenize("") == []

    def test_quoted(self):
        tokens = tokenize('deploy meme --ticker "MY TOKEN"')
        assert "--ticker" in tokens
        assert "MY TOKEN" in tokens


class TestParseArgs:
    def test_flags(self):
        tokens = ["deploy", "meme", "--ticker", "REKT", "--supply", "1000"]
        pos, flags = parse_args(tokens)
        assert pos == ["deploy", "meme"]
        assert flags == {"ticker": "REKT", "supply": "1000"}

    def test_no_flags(self):
        pos, flags = parse_args(["help"])
        assert pos == ["help"]
        assert flags == {}

    def test_boolean_flag(self):
        pos, flags = parse_args(["cmd", "--verbose"])
        assert flags == {"verbose": "true"}


class TestResolveCommand:
    def test_compound(self):
        key, rest = resolve_command(["deploy", "meme"])
        assert key == "deploy_meme"
        assert rest == []

    def test_single(self):
        key, rest = resolve_command(["help"])
        assert key == "help"
        assert rest == []

    def test_empty(self):
        key, rest = resolve_command([])
        assert key == ""


# ─── Command Execution Tests ─────────────────────────────────────────────────


@pytest.fixture
def state():
    return GameState(config=GameConfig(start_capital=10_000))


class TestCommandExecution:
    def test_help(self, state):
        output = execute_command(state, "help")
        assert len(output) > 0
        assert any("help" in line.lower() for line in output)

    def test_status(self, state):
        output = execute_command(state, "status")
        assert len(output) > 0

    def test_wallet(self, state):
        output = execute_command(state, "wallet")
        assert any("USD" in line for line in output)

    def test_deploy_meme(self, state):
        output = execute_command(state, "deploy meme --ticker REKT --supply 1000000")
        assert any("REKT" in line for line in output)
        assert "REKT" in state.tokens
        assert state.wallet.get("REKT") == 1_000_000

    def test_deploy_missing_ticker(self, state):
        output = execute_command(state, "deploy meme --supply 1000")
        assert any("ticker" in line.lower() for line in output)

    def test_pool_create(self, state):
        execute_command(state, "deploy meme --ticker TEST --supply 1000000")
        output = execute_command(
            state, "pool create --token TEST --base-amount 500 --token-amount 500000"
        )
        assert "TEST/USD" in state.pools
        pool = state.pools["TEST/USD"]
        assert pool.reserve_base == 500
        assert pool.reserve_token == 500_000

    def test_trade_buy(self, state):
        execute_command(state, "deploy meme --ticker BUY --supply 1000000")
        execute_command(
            state, "pool create --token BUY --base-amount 1000 --token-amount 500000"
        )
        initial_usd = state.wallet.get("USD")
        output = execute_command(state, "trade buy --market BUY/USD --amount 100")
        assert state.wallet.get("USD") < initial_usd
        assert state.wallet.get("BUY") > 500_000  # got tokens back from pool

    def test_trade_sell(self, state):
        execute_command(state, "deploy meme --ticker SELL --supply 1000000")
        execute_command(
            state, "pool create --token SELL --base-amount 1000 --token-amount 500000"
        )
        tokens_before = state.wallet.get("SELL")
        output = execute_command(state, "trade sell --market SELL/USD --amount 10000")
        assert state.wallet.get("SELL") < tokens_before

    def test_liquidity_pull(self, state):
        execute_command(state, "deploy meme --ticker RUG --supply 1000000")
        execute_command(
            state, "pool create --token RUG --base-amount 500 --token-amount 500000"
        )
        output = execute_command(state, "liquidity pull --market RUG/USD")
        pool = state.pools["RUG/USD"]
        assert pool.reserve_base == 0
        assert pool.reserve_token == 0
        assert any("RUG" in line for line in output)

    def test_unknown_command(self, state):
        output = execute_command(state, "xyzzy")
        assert any("unknown" in line.lower() or "Unknown" in line for line in output)

    def test_heat_increases_on_actions(self, state):
        initial_heat = state.heat.level
        execute_command(state, "deploy meme --ticker HTT --supply 100000")
        assert state.heat.level > initial_heat

    def test_quit(self, state):
        execute_command(state, "quit")
        assert state.running is False

    def test_full_flow(self, state):
        """Test a complete gameplay flow."""
        # Deploy
        execute_command(state, "deploy meme --ticker FLOW --supply 1000000")
        assert "FLOW" in state.tokens

        # Pool
        execute_command(
            state, "pool create --token FLOW --base-amount 1000 --token-amount 500000"
        )
        assert "FLOW/USD" in state.pools

        # Buy
        execute_command(state, "trade buy --market FLOW/USD --amount 200")

        # Status should work
        output = execute_command(state, "status")
        assert len(output) > 0

        # Heat accumulated
        assert state.heat.level > 0
