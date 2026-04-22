# Contributing to sudo-rug

Thanks for the interest. sudo-rug is a hobby project and contributions are welcome — but it's also opinionated. Read this before submitting a PR.

---

## Local Setup

```bash
git clone https://github.com/blairmichaelg/sudo-rug.git
cd sudo-rug

python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"

# Verify tests pass
python -m pytest tests/ -v
```

Requires Python 3.11+.

---

## What Kinds of Contributions Are Welcome

### Strongly welcome
- **Bug fixes** — things that behave differently from the documented simulation rules
- **Test coverage** — edge cases in `sim/amm.py`, heat boundary conditions, wallet arithmetic
- **Balance tuning** — heat costs, decay rates, bot behavior variance — with reasoning
- **New commands** — extending the Phase 1 command set, following the existing handler pattern
- **Event packs** — new random events, heat trigger messages, flavor text in `content/`
- **Documentation** — fixing errors, clarifying mechanics, improving examples

### Probably welcome (open an issue first)
- New simulation systems (mempool, audits, upgrades) — these should match the roadmap
- UI changes — the Textual layout is deliberate; discuss before restructuring
- New game phases — Phase 2 / 3 content is planned but not designed in detail yet

### Not welcome
- Framework dependencies (no Django, FastAPI, click, SQLAlchemy, etc.)
- Real blockchain integration of any kind
- Networking / multiplayer
- Save system complexity beyond basic JSON serialization

---

## Coding Style

- **Python 3.11+** — use `match`, `dataclasses`, type hints where they help
- **Keep modules small** — one responsibility per file, no 500-line god modules
- **No unnecessary abstractions** — if you can do it with a function, don't make a class
- **Prefer clear over clever** — this codebase should be readable by someone who doesn't know Textual
- **Run `python -m pytest` before committing** — don't break the test suite

There's no linter config enforced yet. Use common sense and follow the existing file conventions.

---

## Adding a New Command

1. Write the handler function in `src/sudo_rug/shell/commands.py` following the signature:
   ```python
   def cmd_mycommand(state: GameState, pos: list[str], flags: dict[str, str]) -> list[str]:
   ```
2. Register it in the `COMMANDS` dict at the bottom of that file
3. Add help text for it in `src/sudo_rug/shell/helptext.py`
4. Write at least one test in `tests/test_commands.py`
5. Add it to the command table in `docs/commands.md` and `README.md`

---

## Submitting a PR

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Make your changes
3. Run `python -m pytest tests/ -v` — make sure everything passes
4. Commit with a clear message: `feat: add X`, `fix: heat decay off-by-one`, `docs: clarify rug mechanics`
5. Open a PR with a short description of what changed and why

PRs that break the test suite, add unnecessary complexity, or contradict the project's design philosophy will be closed without merge.
