"""Small HTTP app for demonstrating Kubernetes CPU-based autoscaling."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import socket
import time
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")


class Handler(BaseHTTPRequestHandler):
    server_version = "AutoscaleCloudDemo/" + APP_VERSION

    def _send_json(self, status, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/healthz", "/readyz"):
            self._send_json(200, {"status": "ok", "host": socket.gethostname()})
            return

        if parsed.path == "/work":
            # Bounded CPU work for safely demonstrating an HPA under load.
            params = parse_qs(parsed.query)
            try:
                iterations = int(params.get("iterations", ["250000"])[0])
            except (TypeError, ValueError):
                iterations = 250000
            iterations = max(1000, min(iterations, 2_000_000))
            started = time.perf_counter()
            value = 0
            for i in range(iterations):
                value = (value + (i * i) % 97) % 1000003
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            self._send_json(200, {
                "message": "CPU work completed",
                "host": socket.gethostname(),
                "iterations": iterations,
                "duration_ms": elapsed_ms,
                "result": value,
            })
            return

        if parsed.path == "/":
            self._send_json(200, {
                "project": "Autoscale Cloud Demo",
                "version": APP_VERSION,
                "host": socket.gethostname(),
                "endpoints": {
                    "health": "/healthz",
                    "readiness": "/readyz",
                    "cpu_demo": "/work?iterations=250000",
                },
                "note": "CPU endpoint is for controlled testing in a demo environment.",
            })
            return

        self._send_json(404, {"error": "not_found", "path": parsed.path})

    def log_message(self, fmt, *args):
        # Keep container logs concise and suitable for kubectl logs.
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    print(f"Starting Autoscale Cloud Demo on {HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
