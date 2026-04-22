# Security Policy

## Scope

sudo-rug is a **fictional simulation game**. It connects to no real blockchain, handles no real assets, and makes no external network requests. There is no user authentication, no persistent database, and no server component.

The attack surface of this project is effectively: a local Python application that reads terminal input and simulates a game world.

---

## Reporting a Security Issue

If you find an actual security vulnerability in the codebase itself — for example, unsafe input handling, path traversal in a save file, arbitrary code execution, or a dependency with a known CVE — please report it responsibly:

**Contact:** blairmichaelg@gmail.com  
**Subject line:** `[sudo-rug] Security Issue`

Please include:
- A clear description of the issue
- Steps to reproduce
- The version or commit hash where the issue exists
- Your assessment of severity and exploitability

I'll respond within a reasonable timeframe for a hobby project (typically a few days). If the issue is confirmed, I'll patch it and credit you in the changelog unless you prefer to remain anonymous.

---

## Bug Bounty

There is no bug bounty program. This is a hobby project with no commercial revenue.

---

## Dependency Vulnerabilities

The main dependencies are `textual`, `rich`, `pytest`, and `pytest-asyncio`. If a CVE is published for any of these, feel free to open a GitHub issue or PR updating the version constraint in `pyproject.toml`.
