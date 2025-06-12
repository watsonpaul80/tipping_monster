#!/bin/bash
# Source this script to set TIPPING_MONSTER_HOME to the repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export TIPPING_MONSTER_HOME="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"
