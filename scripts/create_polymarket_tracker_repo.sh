#!/usr/bin/env bash
# =========================
# Polymarket Fresh-Whales Tracker — Repo Bootstrap
# =========================
# 1) Creates a local git repo with this directory as the project root
# 2) Creates a GitHub repo (using gh if installed; else HTTPS+PAT fallback)
# 3) Pushes the initial commit to GitHub (main branch)
#
# The defaults target https://github.com/rabelson97/PolymarketTracker.

set -euo pipefail

# Allow callers to override the defaults without editing the script. This makes it
# easy to point at forks or private mirrors:
#   USERNAME="other" REPO_NAME="ForkedTracker" ./create_polymarket_tracker_repo.sh
#   USERNAME=me VISIBILITY=private ./create_polymarket_tracker_repo.sh
: "${USERNAME:=rabelson97}"
: "${REPO_NAME:=PolymarketTracker}"
: "${VISIBILITY:=public}"

REPO_SLUG="${USERNAME}/${REPO_NAME}"
REMOTE_URL="https://github.com/${REPO_SLUG}.git"

if [[ ! -d .git ]]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "chore: bootstrap minimal Python tracker project"
fi

if command -v gh >/dev/null 2>&1; then
  gh repo create "${REPO_SLUG}" --${VISIBILITY} --source=. --remote=origin --push
else
  if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "ERROR: gh not found and GITHUB_TOKEN not set. Install GitHub CLI or export a PAT." >&2
    exit 1
  fi
  if ! git remote get-url origin >/dev/null 2>&1; then
    AUTH_REMOTE="https://${USERNAME}:${GITHUB_TOKEN}@github.com/${REPO_SLUG}.git"
    git remote add origin "${AUTH_REMOTE}"
  fi
  git push -u origin main
fi

echo "✅ Repo ${REPO_SLUG} created and pushed."
