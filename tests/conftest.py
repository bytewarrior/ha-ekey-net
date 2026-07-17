"""Pytest configuration for the HA-free protocol tests.

Makes the integration's ``protocol`` package importable as a top-level package
without executing the HA-dependent package init
(``custom_components/ekey_net/__init__.py``). This lets the parser tests run
without an installed Home Assistant.
"""

from __future__ import annotations

import pathlib
import sys

_EKEY_NET = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "ekey_net"
sys.path.insert(0, str(_EKEY_NET))
