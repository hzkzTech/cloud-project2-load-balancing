"""Simple backend web service for CISC 7403 Project II.

Two endpoints are provided:
  /       -> identifies the instance that served the request
  /work   -> sleeps for ~50 ms and then answers (used by the benchmark)

The process is started with threaded=False so that one container can serve at
most one /work request at a time.  This keeps the performance experiment fair.
"""

import os
import socket
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

# INSTANCE_NAME is injected through docker-compose (backend1 / backend2).
INSTANCE_NAME = os.environ.get("INSTANCE_NAME") or socket.gethostname()
HOSTNAME = socket.gethostname()
# Simulated processing time of the /work endpoint, in seconds.
WORK_DELAY_SECONDS = float(os.environ.get("WORK_DELAY_SECONDS", "0.05"))
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8000"))


def _log(endpoint: str) -> None:
    """Print one line per request so that 'docker compose logs' shows traffic."""
    app.logger.info(
        "instance=%s pid=%s endpoint=%s client=%s",
        INSTANCE_NAME,
        os.getpid(),
        endpoint,
        request.headers.get("X-Forwarded-For", request.remote_addr),
    )


@app.route("/")
def index():
    _log("/")
    return jsonify(
        instance=INSTANCE_NAME,
        hostname=HOSTNAME,
        pid=os.getpid(),
        endpoint="/",
        message=f"Hello from {INSTANCE_NAME}",
    )


@app.route("/work")
def work():
    started = time.time()
    time.sleep(WORK_DELAY_SECONDS)
    elapsed_ms = round((time.time() - started) * 1000, 1)
    _log("/work")
    return jsonify(
        instance=INSTANCE_NAME,
        hostname=HOSTNAME,
        pid=os.getpid(),
        endpoint="/work",
        work_ms=elapsed_ms,
        message=f"Work done by {INSTANCE_NAME}",
    )


@app.route("/healthz")
def healthz():
    return jsonify(status="ok", instance=INSTANCE_NAME), 200


if __name__ == "__main__":
    # threaded=False -> a single server process handles one request at a time.
    # use_reloader=False -> do not spawn a second process.
    app.run(
        host="0.0.0.0",
        port=LISTEN_PORT,
        threaded=False,
        processes=1,
        debug=False,
        use_reloader=False,
    )
