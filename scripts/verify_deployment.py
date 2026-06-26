#!/usr/bin/env python3
"""Verify deployment connectivity: Frontend -> Backend -> Ollama."""

from __future__ import annotations

import argparse
import os
import sys

import httpx


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Gemma Chatbot deployment connectivity.",
    )
    parser.add_argument(
        "--backend-url",
        default=os.getenv("BACKEND_URL", "").rstrip("/"),
        help="Backend API URL (or set BACKEND_URL env var)",
    )
    parser.add_argument(
        "--frontend-url",
        default=os.getenv("FRONTEND_URL", "").rstrip("/"),
        help="Frontend URL (or set FRONTEND_URL env var)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("VERIFY_TIMEOUT", "30")),
        help="HTTP timeout in seconds",
    )
    args = parser.parse_args()

    if not args.backend_url:
        print("Error: BACKEND_URL is required (env var or --backend-url)", file=sys.stderr)
        return 1

    timeout = httpx.Timeout(args.timeout)
    results: list[bool] = []

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        try:
            response = client.get(f"{args.backend_url}/health")
            data = response.json()
            results.append(
                check(
                    "Backend /health",
                    response.status_code == 200 and data.get("status") == "healthy",
                    f"status={response.status_code} body={data}",
                )
            )
        except Exception as exc:
            results.append(check("Backend /health", False, str(exc)))

        try:
            response = client.get(f"{args.backend_url}/health/model")
            data = response.json()
            healthy = (
                response.status_code == 200
                and data.get("status") == "healthy"
                and data.get("ollama") == "reachable"
                and data.get("model_loaded") is True
            )
            results.append(
                check(
                    "Backend /health/model (Ollama)",
                    healthy,
                    f"status={response.status_code} body={data}",
                )
            )
        except Exception as exc:
            results.append(check("Backend /health/model (Ollama)", False, str(exc)))

        if args.frontend_url:
            try:
                response = client.get(args.frontend_url)
                results.append(
                    check(
                        "Frontend reachable",
                        response.status_code == 200,
                        f"status={response.status_code}",
                    )
                )
            except Exception as exc:
                results.append(check("Frontend reachable", False, str(exc)))
        else:
            print("[SKIP] Frontend — set FRONTEND_URL or --frontend-url to test")

    passed = all(results)
    print()
    print("All checks passed." if passed else "Some checks failed.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
