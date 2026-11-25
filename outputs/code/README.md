# CISC 7403 Project II — Scalable Web Service with Load Balancing

Three containers: one Nginx load balancer (`lb`, host port **6120**) and two
identical Flask backends (`backend1`, `backend2`) built from the same image
`cisc7403/backend:1.0`.

```
.
├── backend/
│   ├── app.py              # Flask service: "/" and "/work" (50 ms), threaded=False
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── nginx/
│   ├── nginx.conf          # 2-upstream pool (normal deployment)
│   └── nginx.single.conf   # 1-upstream pool (performance comparison only)
├── scripts/
│   ├── verify_lb.sh        # load-balancing evidence
│   ├── fault_tolerance.sh  # guided stop/restart walkthrough
│   └── bench.sh            # wrk benchmark for 2 vs 1 backend
├── docker-compose.yml          # lb + backend1 + backend2
└── docker-compose.single.yml   # lb + backend1

## Run

```bash
docker compose up --build        # start the 3-container system
curl http://localhost:6120/      # {"instance": "backend1" | "backend2", ...}
curl http://localhost:6120/work  # same, after ~50 ms of simulated work
docker compose logs -f           # per-request logs from all containers
docker compose down
```

Only `lb` publishes a port (`6120`). The backends publish nothing and are
reached by service name (`backend1:8000`, `backend2:8000`) over the user-defined
bridge network `appnet`.

Benchmark (needs `wrk`):

```bash
./scripts/bench.sh               # 2 backends, then 1 backend, same workload
```
