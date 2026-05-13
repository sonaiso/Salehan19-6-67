#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

PYTHONPATH=src:. python -m mcd.cli pilot-readiness --output json
PYTHONPATH=src:. python -m mcd.cli governance-replay --output json
PYTHONPATH=src:. python -m mcd.cli math-global-certificate --output json

