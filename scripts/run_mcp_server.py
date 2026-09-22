#!/usr/bin/env python3
"""Run Laya MCP from a catalog checkout with isolated target dependencies."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / ".mcp-deps"
for path in (DEPS, ROOT):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from laya.mcp_server import main

if __name__ == "__main__":
    main()
