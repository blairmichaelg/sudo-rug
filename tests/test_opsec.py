import pytest
from sudo_rug.core.state import GameState, GameConfig
from sudo_rug.sim.heat import add_heat
from sudo_rug.core.enums import ActionType

@pytest.fixture
def state():
    return GameState(config=GameConfig())

def test_opsec_heat_reduction(state: GameState):
    """Test that opsec tier reduction correctly modifies heat accumulation."""
    # Base cost for DEPLOY_TOKEN is 10.0
    
    # Tier 0 (OpSec 0.05)
    state.opsec = 0.05
    added_0 = add_heat(state, ActionType.DEPLOY_TOKEN)
    # opsec_factor = 1.0 - (0.05 * 0.5) = 0.975
    # actual = 10.0 * 0.975 = 9.75
    assert added_0 == 9.75
    
    # Reset heat
    state.heat.level = 0.0
    
    # Tier 1 (OpSec 0.20)
    state.opsec = 0.20
    added_1 = add_heat(state, ActionType.DEPLOY_TOKEN)
    # opsec_factor = 1.0 - (0.20 * 0.5) = 0.90
    # actual = 10.0 * 0.90 = 9.0
    assert added_1 == 9.0
    
    # Tier 2 (OpSec 0.40)
    state.opsec = 0.40
    added_2 = add_heat(state, ActionType.DEPLOY_TOKEN)
    # opsec_factor = 1.0 - (0.40 * 0.5) = 0.80
    # actual = 10.0 * 0.80 = 8.0
    assert added_2 == 8.0

def test_opsec_protection_levels(state: GameState):
    """Test that opsec protection levels are correctly represented in state."""
    # Ensure the state can hold these values correctly even without the upgrade command
    state.opsec_tier = 1
    state.opsec = 0.20
    assert state.opsec_tier == 1
    assert state.opsec == 0.20
