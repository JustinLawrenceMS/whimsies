#!/usr/bin/env bash
set -euo pipefail

echo "This script will remove .env from git tracking and create a commit.
It does NOT rewrite git history. To purge .env from history see REDACT_INSTRUCTIONS.md."

if [ ! -d .git ]; then
  echo "Not a git repository (no .git). Run this from your repo root." >&2
  exit 1
fi

if [ -f .env ]; then
  echo "Removing .env from git tracking..."
  git rm --cached .env || true
else
  echo ".env not present in working tree; ensuring it's removed from index if present..."
  git rm --cached --ignore-unmatch .env || true
fi

git add .gitignore || true
git commit -m "chore: remove .env from repo and add to .gitignore" || echo "Nothing to commit"

echo "Done. If you need to remove secrets from git history, follow REDACT_INSTRUCTIONS.md"
