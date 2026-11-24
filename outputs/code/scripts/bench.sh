#!/usr/bin/env bash
# Performance experiment: run the SAME wrk workload against the 2-backend stack
# and then against the 1-backend stack, saving both raw outputs under results/.
#
#   ./scripts/bench.sh
#   DURATION=10s THREADS=2 CONN=20 ./scripts/bench.sh
set -euo pipefail
cd "$(dirname "$0")/.."

THREADS="${THREADS:-2}"
CONN="${CONN:-20}"
DURATION="${DURATION:-10s}"
URL="${URL:-http://localhost:6120/work}"
RESULTS_DIR="${RESULTS_DIR:-results}"

command -v wrk >/dev/null 2>&1 || {
  echo "wrk not found. Install it first:  sudo apt update && sudo apt install -y wrk" >&2
  exit 1
}

mkdir -p "${RESULTS_DIR}"
WORKLOAD="-t${THREADS} -c${CONN} -d${DURATION}"

echo "=============================================================="
echo " Configuration A: 2 backends"
echo "=============================================================="
docker compose -f docker-compose.single.yml down 2>/dev/null || true
docker compose -f docker-compose.yml up -d --build
sleep 5
docker compose -f docker-compose.yml ps
wrk ${WORKLOAD} "${URL}" | tee "${RESULTS_DIR}/wrk_2backends.txt"

echo
echo "=============================================================="
echo " Configuration B: 1 backend"
echo "=============================================================="
docker compose -f docker-compose.yml down
docker compose -f docker-compose.single.yml up -d --build
sleep 5
docker compose -f docker-compose.single.yml ps
wrk ${WORKLOAD} "${URL}" | tee "${RESULTS_DIR}/wrk_1backend.txt"

echo
echo "Raw results saved to:"
echo "  ${RESULTS_DIR}/wrk_2backends.txt"
echo "  ${RESULTS_DIR}/wrk_1backend.txt"
echo
echo "Restoring the 2-backend deployment..."
docker compose -f docker-compose.single.yml down
docker compose -f docker-compose.yml up -d
