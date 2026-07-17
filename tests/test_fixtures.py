"""Byte verification against real ekey net packets.

The fixtures come from a real capture of an ekey net system (terminal server
UDP transmission, ``rare`` format). They prove that the parser decodes the
actual hardware encoding correctly (offsets, little-endian, 14-digit serial,
UTF-16LE name).

The user name in the access fixture has been anonymized. The event code stored
inside the reject fixture reflects the raw bytes as sent by a device configured
in German.
"""

from __future__ import annotations

import pathlib

from protocol import parse

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _load(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


def test_real_reject_unknown_finger():
    """Packet 1: unknown/rejected finger."""
    ev = parse(_load("rare_terminal_reject_unknown.bin"))
    assert ev is not None
    assert ev.source_format == "rare"
    assert ev.packet_version == 3
    assert ev.action_code == 4
    assert ev.action_name == "Unknown finger"
    assert ev.ha_event_type == "access_denied_unknown"
    assert ev.serial == "80290510220655"
    assert ev.user_id is None
    assert ev.finger_id == 1
    # Raw event string as sent by the device (configured in German).
    assert ev.event_code == "Ablehnung: unbe"
    assert ev.timestamp is not None
    assert (ev.timestamp.year, ev.timestamp.month, ev.timestamp.day) == (2026, 7, 16)


def test_real_access_granted_left_middle_finger():
    """Packet 2: recognized left middle finger -> access (name anonymized)."""
    ev = parse(_load("rare_terminal_access_granted.bin"))
    assert ev is not None
    assert ev.source_format == "rare"
    assert ev.action_code == 1
    assert ev.action_name == "Entry"
    assert ev.ha_event_type == "access_granted"
    assert ev.serial == "80290510220655"
    assert ev.user_id == 1
    assert ev.user_name == "Mustermann, Max"
    assert ev.finger_id == 3
    assert ev.finger_name == "Left middle finger"
    assert ev.timestamp is not None
