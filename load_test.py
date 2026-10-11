#!/usr/bin/env python3
"""Simple standard-library concurrent load tester; use only against your own demo."""
import argparse
import concurrent.futures
import time
import urllib.error
import urllib.request


def hit(url, timeout):
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            response.read()
            return response.status, (time.perf_counter() - started) * 1000
    except urllib.error.HTTPError as exc:
        return exc.code, (time.perf_counter() - started) * 1000
    except Exception:
        return 0, (time.perf_counter() - started) * 1000


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://127.0.0.1:8080/work?iterations=250000")
    p.add_argument("--requests", type=int, default=100)
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--timeout", type=float, default=10.0)
    args = p.parse_args()
    if args.requests < 1 or args.workers < 1:
        p.error("--requests and --workers must be positive")

    started = time.perf_counter()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(hit, args.url, args.timeout) for _ in range(args.requests)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
    duration = time.perf_counter() - started
    statuses = {}
    latencies = []
    for status, ms in results:
        statuses[status] = statuses.get(status, 0) + 1
        latencies.append(ms)
    latencies.sort()
    p95 = latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))]
    print(f"Target: {args.url}")
    print(f"Requests: {len(results)} | workers: {args.workers} | elapsed: {duration:.2f}s")
    print(f"Throughput: {len(results) / duration:.2f} requests/sec | p95 latency: {p95:.1f} ms")
    print("Statuses:", ", ".join(f"{k if k else 'connection-error'}={v}" for k, v in sorted(statuses.items(), key=lambda x: str(x[0]))))
    print("For HPA observation, run: kubectl get hpa,pods -n autoscale-demo -w")


if __name__ == "__main__":
    main()
