#!/usr/bin/env bash
# Guided fault-tolerance walkthrough.  Each stage pauses so that a screenshot
# can be taken in between.
#
#   ./scripts/fault_tolerance.sh
set -euo pipefail
cd "$(dirname "$0")/.."

URL="${URL:-http://localhost:6120/}"
ROUNDS="${ROUNDS:-6}"

pause() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    Press Enter to continue..." _
}

hit() {
  for i in $(seq 1 "${ROUNDS}"); do
    printf '  [%2d] %s\n' "${i}" "$(curl -s --max-time 5 "${URL}" || echo 'REQUEST FAILED')"
  done
}

echo "=== Stage 0: current container status ==="
docker compose ps

pause "Stage 1: both backends alive - requests should alternate between backend1 and backend2"
hit

pause "Stage 2: stopping backend2 (docker stop backend2)"
docker stop backend2
docker compose ps

pause "Stage 3: service must still answer, now only from backend1"
hit

pause "Stage 4: restarting backend2 (docker start backend2)"
docker start backend2
sleep 4
docker compose ps

pause "Stage 5: both backends back in the pool"
hit

echo
echo "=== Done ==="
