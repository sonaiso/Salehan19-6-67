#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

PYTHONPATH=src:. python -m mcd.cli api-schema-check --output json
PYTHONPATH=src:. python -m mcd.cli source-api-smoke --scenario ok_with_relevant_docs --output json
PYTHONPATH=src:. python -m mcd.cli source-api-smoke --scenario timeout --output json

