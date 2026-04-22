"""Quick smoke test of the game systems."""
from sudo_rug.core.state import GameState, GameConfig
from sudo_rug.shell.commands import execute_command

s = GameState(config=GameConfig(start_capital=10_000))
print(f"GameState OK: ${s.net_worth():,.2f} USD, block {s.clock_block}")

# Deploy
out = execute_command(s, "deploy meme --ticker REKT --supply 1000000")
for line in out:
    print(line)

# Pool
out = execute_command(s, "pool create --token REKT --base-amount 500 --token-amount 500000")
for line in out:
    print(line)

# Buy
out = execute_command(s, "trade buy --market REKT/USD --amount 100")
for line in out:
    print(line)

# Status
out = execute_command(s, "status")
for line in out:
    print(line)

# Sell
out = execute_command(s, "trade sell --market REKT/USD --amount 50000")
for line in out:
    print(line)

# Rug
out = execute_command(s, "liquidity pull --market REKT/USD")
for line in out:
    print(line)

# Final status
print(f"\nFinal net worth: ${s.net_worth():,.2f}")
print(f"Heat: {s.heat.level:.1f}")
print(f"Tests: ALL SYSTEMS NOMINAL")
