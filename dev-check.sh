#!/bin/bash
# Dev environment sanity check for Tipping Monster
# Verifies Python version, virtualenv activation, .env file, and essential files.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ERR=0

print_ok() { echo "[OK] $1"; }
print_err() { echo "[ERROR] $1"; ERR=1; }

# Check Python version >= 3.9
PYTHON="$(command -v python3 || command -v python)"
if [ -z "$PYTHON" ]; then
  print_err "Python not found in PATH"
else
  VERSION_OK=$($PYTHON - <<'PY'
import sys
print(1 if sys.version_info >= (3,9) else 0)
PY
)
  if [ "$VERSION_OK" = "1" ]; then
    VER=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    print_ok "Python version $VER"
  else
    print_err "Python 3.9+ required"
  fi
fi

# Check .venv directory
if [ -d ".venv" ]; then
  print_ok ".venv directory exists"
else
  print_err ".venv directory missing"
fi

# Check that venv is activated
if [ -n "$VIRTUAL_ENV" ]; then
  print_ok "virtual environment activated"
else
  print_err "activate your virtualenv (. ./venv/bin/activate)"
fi

# Check .env file
if [ -f ".env" ]; then
  print_ok ".env file present"
else
  print_err ".env file missing"
fi

# Required files
REQUIRED=("features.json" "lifecycle.json" "requirements.txt")
for f in "${REQUIRED[@]}"; do
  if [ -f "$f" ]; then
    print_ok "$f present"
  else
    print_err "missing $f"
  fi
done

if [ "$ERR" -eq 0 ]; then
  echo "All checks passed."
else
  echo "Environment check failed." >&2
  exit 1
fi
