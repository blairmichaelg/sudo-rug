import pytest
import json
from sudo_rug.core.state import GameState, Token, Pool, BotJob, GameConfig

@pytest.fixture
def state():
    return GameState(config=GameConfig())

def test_state_to_dict_and_back(state: GameState):
    """Test roundtrip JSON serialization of complex GameState."""
    state.clock_block = 42
    state.heat.level = 50.0
    state.opsec_tier = 2
    state.wallet.credit("USD", 5000.0)
    state.wallet.credit("REKT", 100.0)
    
    # Add token
    state.tokens["REKT"] = Token(ticker="REKT", total_supply=1000.0, block_created=10)
    
    # Add pool
    state.pools["REKT/USD"] = Pool(token="REKT", base="USD", reserve_token=500.0, reserve_base=250.0)
    
    # Add bot
    state.bots.append(BotJob(budget_remaining=100.0, budget_total=200.0, blocks_remaining=5, blocks_total=10, market="REKT/USD"))
    
    # Serialized
    state_dict = state.to_dict()
    json_str = json.dumps(state_dict)
    
    # Deserialized
    recovered_data = json.loads(json_str)
    new_state = GameState.from_dict(recovered_data)
    
    assert new_state.clock_block == 42
    assert new_state.heat.level == 50.0
    assert new_state.opsec_tier == 2
    assert new_state.wallet.get("USD") == 6000.0
    assert new_state.wallet.get("REKT") == 100.0
    
    # Complex objects
    assert "REKT" in new_state.tokens
    assert new_state.tokens["REKT"].total_supply == 1000.0
    
    assert "REKT/USD" in new_state.pools
    assert new_state.pools["REKT/USD"].reserve_token == 500.0
    
    assert len(new_state.bots) == 1
    assert new_state.bots[0].market == "REKT/USD"
    assert new_state.bots[0].budget_remaining == 100.0

def test_save_load_commands(state: GameState, tmp_path, monkeypatch):
    """Test the save and load commands logic."""
    from sudo_rug.shell.commands import cmd_save, cmd_load
    
    # Monkeypatch the save path to use tmp_path
    save_dir = tmp_path / ".sudo_rug"
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    
    # Modify state to be identifiable
    state.clock_block = 999
    
    # Issue save
    save_res = cmd_save(state, [], {})
    assert "Game saved" in "".join(save_res)
    assert (save_dir / "save.json").exists()
    
    # Issue load
    load_res = cmd_load(state, [], {})
    assert load_res[0].startswith("__LOAD_JSON__")
    
    # Parse back the json embedded in the command return
    json_str = load_res[0].split("\n", 1)[1]
    data = json.loads(json_str)
    assert data["clock_block"] == 999
