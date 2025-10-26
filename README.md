# Polymarket Fresh-Whales Tracker

This directory contains a self-contained Python project that can be promoted to its own Git repository.
It packages the production tracker implementation, dependency manifest, and supporting bootstrap script
so you can spin up a dedicated repo without touching the surrounding monorepo. The layout and helper
script are now aligned with <https://github.com/rabelson97/PolymarketTracker> so you can push these
exact files to that repository with no further renaming.

## 📁 What's inside

| File | Purpose |
| --- | --- |
| `polymarket_fresh_whales_tracker.py` | Full tracker implementation with API, Web3, and CSV export support. |
| `requirements.txt` | Minimal dependency set (`requests`, `web3`). |
| `.gitignore` | Ignores Python build artifacts, virtualenvs, IDE settings, and CSV exports. |
| `LICENSE` | MIT license stub – update the copyright notice before publishing. |
| `scripts/create_polymarket_tracker_repo.sh` | Optional helper that creates and pushes a standalone GitHub repo using this folder as the source. |

## 🚀 Bootstrap a dedicated repository

If you want to publish this tracker on GitHub (or any remote), run the helper script below. It mirrors the
workflow described in the original bootstrap documentation:

```bash
cd PolymarketTracker
chmod +x scripts/create_polymarket_tracker_repo.sh
./scripts/create_polymarket_tracker_repo.sh
```

By default the script targets `https://github.com/rabelson97/PolymarketTracker`. You can reuse the
same helper for forks or private mirrors by overriding the environment variables before execution:

```bash
# Example: publish to a personal fork
USERNAME="my-handle" REPO_NAME="PolymarketTracker" ./scripts/create_polymarket_tracker_repo.sh

# Example: create a private copy without using the GitHub CLI
USERNAME="my-handle" REPO_NAME="FreshTracker" VISIBILITY="private" \
  GITHUB_TOKEN="<classic PAT with repo scope>" ./scripts/create_polymarket_tracker_repo.sh
```

If you already have the repository `rabelson97/PolymarketTracker` provisioned on GitHub, simply run the
script inside this directory and it will push the current contents to that remote.

The script expects one of the following authentication methods:

- Logged-in GitHub CLI (`gh auth login`), **or**
- `GITHUB_TOKEN` environment variable with `repo` scope (used as a fallback when `gh` is unavailable).

You can also perform the steps manually:

```bash
cd PolymarketTracker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
git init -b main
git add .
git commit -m "feat: initial tracker import"
gh repo create rabelson97/PolymarketTracker --public --source=. --remote=origin --push
```

Alternatively, wire up the remote yourself and push:

```bash
git remote add origin git@github.com:rabelson97/PolymarketTracker.git
git push -u origin main
```

## 🧪 Local usage

```bash
cd PolymarketTracker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export POLYGON_RPC_URL="https://your-polygon-rpc.example"
export POLYMARKET_SESSION_TOKEN="pm-access-token-cookie"
python polymarket_fresh_whales_tracker.py --limit 500 --min-cash 5000 --min-balance 50000 --fresh-max-prior-tx 3 --csv matches.csv
```

See `python polymarket_fresh_whales_tracker.py --help` for a complete description of the available CLI flags.
