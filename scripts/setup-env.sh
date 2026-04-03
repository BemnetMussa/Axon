#!/usr/bin/env bash
# Create backend/.env and fronted/.env from *.example if they do not exist.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

copy_if_missing() {
	local dest="$1"
	local example="$2"
	if [[ -f "$dest" ]]; then
		echo "skip (already exists): $dest"
	else
		cp "$example" "$dest"
		echo "created: $dest — add real secrets (GROQ_API_KEY, Google OAuth, etc.)"
	fi
}

copy_if_missing "$ROOT/backend/.env" "$ROOT/backend/.env.example"
copy_if_missing "$ROOT/fronted/.env" "$ROOT/fronted/.env.example"
echo "Done."
