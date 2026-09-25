#!/usr/bin/env bash
# Export a clean public tree for a NEW open-source GitHub repo.
# Does NOT push. Does NOT include secrets, private/, or .git history.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-/tmp/axon-oss-export}"

echo "Exporting clean OSS tree from: $ROOT"
echo "Output: $OUT"

rm -rf "$OUT"
mkdir -p "$OUT"

# Copy tracked-like tree while excluding secrets and proprietary overlay
rsync -a \
  --exclude '.git/' \
  --exclude 'private/services/' \
  --exclude '**/node_modules/' \
  --exclude '**/.venv/' \
  --exclude '**/venv/' \
  --exclude '**/.svelte-kit/' \
  --exclude '**/build/' \
  --exclude '**/.vercel/' \
  --exclude '**/.env' \
  --exclude '**/.env.*' \
  --exclude '!**/.env.example' \
  --exclude '.cursor/' \
  --exclude '.claude/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  "$ROOT/" "$OUT/"

# Belt-and-suspenders: wipe any env files that slipped through
find "$OUT" -type f \( -name '.env' -o -name '.env.*' \) ! -name '.env.example' -delete
rm -rf "$OUT/private/services" 2>/dev/null || true

# Sanity checks
if find "$OUT" -type f \( -name '.env' -o -path '*/private/services/*' \) | grep -q .; then
  echo "ERROR: secrets or private engine found in export" >&2
  find "$OUT" -type f \( -name '.env' -o -path '*/private/services/*' \) >&2
  exit 1
fi

# Ignore UI form state, env getters, and known dummy CI keys
if grep -RInE --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.svelte-kit \
  'gsk_[A-Za-z0-9]{20,}|sk-(live|proj)-[A-Za-z0-9]{20,}' \
  "$OUT" 2>/dev/null \
  | grep -Ev 'gsk_(ci_dummy|test_dummy)|.env.example' \
  | head -5 | grep -q .; then
  echo "WARNING: possible real API key-looking strings — review before publishing" >&2
fi

echo
echo "Clean export ready at: $OUT"
echo "Next (you run these — nothing is pushed automatically):"
echo "  cd $OUT && git init && git add . && git commit -m 'Initial open-core release'"
echo "  gh repo create BemnetMussa/Axon --public --source=. --remote=origin --push"
echo
echo "Keep the existing private repo private (it still has proprietary history),"
echo "or scrub history with git filter-repo before flipping visibility."
