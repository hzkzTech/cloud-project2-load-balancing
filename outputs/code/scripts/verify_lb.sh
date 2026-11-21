#!/usr/bin/env bash
# Load-balancing verification: send N requests through the Nginx load balancer,
# show which backend answered each one, then print a per-instance tally.
#
#   ./scripts/verify_lb.sh
#   N=20 URL=http://localhost:6120/work ./scripts/verify_lb.sh
set -euo pipefail

URL="${URL:-http://localhost:6120/}"
N="${N:-10}"

echo "==> Sending ${N} requests to ${URL}"
all=""
for i in $(seq 1 "${N}"); do
  body="$(curl -s --max-time 5 "${URL}")"
  inst="$(printf '%s' "${body}" | grep -o '"instance":[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')"
  printf '[%2d] %-12s %s\n' "${i}" "${inst:-?}" "${body}"
  all="${all}${inst}"$'\n'
done

echo
echo "==> Per-instance tally"
printf '%s' "${all}" | sed '/^$/d' | sort | uniq -c
