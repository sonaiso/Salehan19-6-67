"""Allow ``python -m mcd.llm_proposer`` invocation."""
from __future__ import annotations

import sys

from mcd.llm_proposer.cli import main

sys.exit(main())
