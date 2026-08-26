#!/usr/bin/env bash
# Launch prep: refresh prod feed + print a short health report.
# Usage (from repo root):
#   export AXON_API_URL='https://your-api.example.com'
#   export AXON_INTERNAL_SECRET='...'   # same as prod
#   ./scripts/launch-prep.sh
#
# Or put both in a local (gitignored) file and:  set -a; source .env.launch; set +a

set -euo pipefail

API="${AXON_API_URL:-${INTERNAL_API_URL:-}}"
SECRET="${AXON_INTERNAL_SECRET:-}"
USER_ID="${CRON_INGEST_USER_ID:-launch-prep}"

if [[ -z "$API" || -z "$SECRET" ]]; then
  echo "Set AXON_API_URL (or INTERNAL_API_URL) and AXON_INTERNAL_SECRET first."
  echo "Get INTERNAL_API_URL from Vercel → Project → Settings → Environment Variables."
  exit 1
fi

API="${API%/}"
HDR=(-H "X-Axon-Internal-Secret: $SECRET" -H "X-Axon-User-Id: $USER_ID")

echo "== Health =="
curl -sS "$API/health" | python3 -m json.tool || curl -sS "$API/health"
echo

echo "== Ingest (force) =="
curl -sS -X POST "${API}/ingest?force=true" "${HDR[@]}" | python3 -m json.tool
echo

echo "== Analyze =="
curl -sS -X POST "${API}/analyze" "${HDR[@]}" | python3 -m json.tool
echo

echo "== Sample feed (5) =="
curl -sS "${API}/articles?limit=5" "${HDR[@]}" \
  | python3 -c '
import json,sys
d=json.load(sys.stdin)
arts=d.get("articles") or d if isinstance(d,list) else []
print(f"count_in_page={len(arts)}")
for a in arts[:5]:
    title=(a.get("title") or "")[:70]
    src=a.get("source")
    ins="yes" if a.get("insight") else "no"
    print(f"- [{src}] {title} | insight={ins}")
'
echo
echo "Done. Open https://axon-phi-ruby.vercel.app/app and spot-check the feed."
