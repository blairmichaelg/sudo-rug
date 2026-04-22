import pytest
from sudo_rug.core.state import GameState, GameConfig
from sudo_rug.shell.commands import cmd_opsec_upgrade
from sudo_rug.core.enums import ActionType

@pytest.fixture
def state():
    return GameState(config=GameConfig())

def test_opsec_upgrade_tier1(state: GameState):
    """Test purchasing Tier 1 successful."""
    state.wallet.credit("USD", 1000.0)
    res = cmd_opsec_upgrade(state, [], {"tier": "1"})
    
    assert "OpSec upgraded to Tier 1" in "".join(res)
    assert state.opsec_tier == 1
    assert state.opsec == 0.20
    assert state.wallet.get("USD") == 1500.0  # 1000 start + 1000 credit - 500 cost

def test_opsec_upgrade_out_of_order(state: GameState):
    """Test purchasing Tier 2 without Tier 1 fails."""
    state.wallet.credit("USD", 5000.0)
    res = cmd_opsec_upgrade(state, [], {"tier": "2"})
    
    assert "Must purchase tiers in order" in "".join(res)
    assert state.opsec_tier == 0
    
def test_opsec_upgrade_insufficient_funds(state: GameState):
    """Test purchasing Tier 1 without enough funds fails."""
    state.wallet.balances["USD"] = 100.0  # Reset below 500 cost
    res = cmd_opsec_upgrade(state, [], {"tier": "1"})
    
    assert "Insufficient USD" in "".join(res)
    assert state.opsec_tier == 0

def test_opsec_upgrade_heat_lockdown(state: GameState):
    """Test that opsec upgrade is disabled during heat lockdown."""
    state.wallet.credit("USD", 5000.0)
    state.heat.level = 95.0
    res = cmd_opsec_upgrade(state, [], {"tier": "1"})
    assert "LOCKDOWN" in "".join(res)
    assert state.opsec_tier == 0
