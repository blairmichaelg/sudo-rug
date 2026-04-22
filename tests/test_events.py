import pytest
from sudo_rug.core.state import GameState, GameConfig
from sudo_rug.core.events import check_random_events

@pytest.fixture
def state():
    return GameState(config=GameConfig())

def test_check_random_events_empty_wallet(state: GameState):
    """Test that random events don't trigger if the player has nothing to lose."""
    # Base state has 1000 USD and no tokens. The condition says:
    # if not state.tokens and state.wallet.get("USD") == state.config.start_capital:
    #     return messages
    assert len(check_random_events(state)) == 0

def test_check_random_events_mev_drain(state: GameState, monkeypatch):
    """Test the MEV Sandwich Attack event (loss of USD)."""
    # 0.005 triggers MEV event (roll < 0.01)
    monkeypatch.setattr("random.random", lambda: 0.005)
    
    # Must have something deployed or non-start USD amount
    state.wallet.credit("USD", 100.0) # Now at 1100.0
    initial_usd = state.wallet.get("USD")
    
    msgs = check_random_events(state)
    assert len(msgs) == 1
    assert "MEV bots frontran your activity" in msgs[0]
    
    # Needs to have lost some money
    assert state.wallet.get("USD") < initial_usd

def test_check_random_events_viral_tweet(state: GameState, monkeypatch):
    """Test Viral Tweet (Heat +10)"""
    monkeypatch.setattr("random.random", lambda: 0.012)
    state.wallet.debit("USD", 100.0)
    
    # Needs an active pool to trigger
    from sudo_rug.core.state import Pool
    state.pools["TEST/USD"] = Pool(token="TEST", base="USD", reserve_token=1000.0, reserve_base=100.0)
    
    initial_heat = state.heat.level
    
    msgs = check_random_events(state)
    assert len(msgs) == 1
    assert "An influencer tweeted" in msgs[0]
    assert state.heat.level == initial_heat + 10.0

def test_check_random_events_lucky_break(state: GameState, monkeypatch):
    """Test sleuth debunked (Heat -15)"""
    monkeypatch.setattr("random.random", lambda: 0.018)
    state.wallet.debit("USD", 100.0)
    state.heat.level = 30.0
    
    msgs = check_random_events(state)
    assert len(msgs) == 1
    assert "An on-chain sleuth" in msgs[0]
    assert state.heat.level == 15.0
