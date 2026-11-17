"""Small Flask service used as the workload for the CI/CD pipeline."""
import os
import random
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "dev")

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["endpoint"]
)


@app.before_request
def _start_timer():
    request.environ["_start"] = time.perf_counter()


@app.after_request
def _record_metrics(response):
    endpoint = request.url_rule.rule if request.url_rule else "unmatched"
    start = request.environ.get("_start", time.perf_counter())
    LATENCY.labels(endpoint).observe(time.perf_counter() - start)
    REQUESTS.labels(request.method, endpoint, response.status_code).inc()
    return response


@app.get("/")
def index():
    return jsonify(message="Hello from the DevOps demo app", version=VERSION)


@app.get("/health")
def health():
    """Liveness probe: the process is up."""
    return jsonify(status="ok")


@app.get("/ready")
def ready():
    """Readiness probe: the app can take traffic."""
    return jsonify(status="ready")


@app.get("/slow")
def slow():
    """Random latency, useful for demoing latency alerts."""
    time.sleep(random.uniform(0.1, 1.5))
    return jsonify(status="slow but ok")


@app.get("/flaky")
def flaky():
    """Fails ~30% of the time, useful for demoing error-rate alerts."""
    if random.random() < 0.3:
        return jsonify(error="simulated failure"), 500
    return jsonify(status="ok")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
