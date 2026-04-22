from sudo_rug.app import run_app
from sudo_rug.core.state import GameState
from sudo_rug.content.starter_scenarios import default_config

def main():
    config = default_config()
    state = GameState(config=config)
    run_app(state)

if __name__ == "__main__":
    main()
