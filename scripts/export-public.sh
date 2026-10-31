#!/usr/bin/env bash
# Build the public Axon repo: committed files from HEAD, minus the hosted
# prompts, as a single commit with no history (old commits contain the prompts).
#
#   scripts/export-public.sh <out-dir> [public-remote-url]
#
# With a remote URL, force-pushes the fresh commit to its main branch.
set -euo pipefail

OUT="${1:?usage: export-public.sh <out-dir> [public-remote-url]}"
REMOTE="${2:-}"
ROOT="$(git rev-parse --show-toplevel)"

EXCLUDE=(
  backend/engine/prompts_hosted.py
  scripts/export-public.sh
)

# Phrases that only appear in the hosted prompts. If any shows up in the
# export, a prompt leaked into another file and the export is aborted.
CANARIES=(
  "Lead Intelligence Analyst"
  "Lead Intelligence Editor"
  "Technical Primitive: (Describe"
  "You write briefs for Axon"
  "Axon's reading assistant"
)

rm -rf "$OUT"
mkdir -p "$OUT"
git -C "$ROOT" archive HEAD | tar -x -C "$OUT"
for path in "${EXCLUDE[@]}"; do
  rm -f "$OUT/$path"
done

for phrase in "${CANARIES[@]}"; do
  if grep -rqF "$phrase" "$OUT"; then
    echo "ABORT: hosted prompt text found in export: \"$phrase\"" >&2
    grep -rlF "$phrase" "$OUT" >&2
    exit 1
  fi
done

cd "$OUT"
git init -q -b main
git add -A
git commit -q -m "Axon: open-source release"
echo "Exported $(git ls-files | wc -l) files to $OUT"

if [[ -n "$REMOTE" ]]; then
  git remote add origin "$REMOTE"
  git push -f -u origin main
fi
