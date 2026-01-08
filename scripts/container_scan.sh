#!/usr/bin/env bash
set -euo pipefail

echo "== OpsHub container scan (best-effort) =="

echo
if command -v trivy >/dev/null 2>&1; then
  echo "-- Trivy filesystem scan --"
  trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --no-progress . || true
else
  echo "trivy not installed. Install from https://aquasecurity.github.io/trivy/" >&2
fi

echo
if command -v docker >/dev/null 2>&1; then
  echo "-- Docker build + scan (optional) --"
  echo "Build: docker build -t opshub:local -f app/Dockerfile ."
  echo "Then scan: trivy image opshub:local"
else
  echo "docker not found; skipping build instructions." >&2
fi

echo
echo "Done."