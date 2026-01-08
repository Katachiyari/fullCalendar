#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python="${PYTHON:-$ROOT_DIR/venv/bin/python}"

echo "== OpsHub security scan (best-effort) =="

if [[ -x "$python" ]]; then
  echo "Using python: $python"
else
  echo "Python not found at $python. Set PYTHON env var." >&2
  exit 1
fi

echo

echo "-- SCA (Python): pip-audit --"
if "$python" -m pip_audit --version >/dev/null 2>&1; then
  "$python" -m pip_audit -r app/requirements.txt || true
else
  echo "pip-audit not installed. Install: $python -m pip install pip-audit" >&2
fi

echo

echo "-- SAST (Python): bandit --"
if "$python" -m bandit --version >/dev/null 2>&1; then
  "$python" -m bandit -q -r app || true
else
  echo "bandit not installed. Install: $python -m pip install bandit" >&2
fi

echo

echo "-- Secrets scan: gitleaks (optional) --"
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --source . --no-git --redact || true
else
  echo "gitleaks not installed (optional)." >&2
fi

echo

echo "-- Node audit (optional; requires npm) --"
if command -v npm >/dev/null 2>&1; then
  (cd frontend && npm audit --audit-level=moderate) || true
else
  echo "npm not found; skipping frontend audit." >&2
fi

echo

echo "Done. Review findings above."