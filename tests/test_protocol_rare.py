"""Unit tests for the binary rare/rare-v2 parser.

The fixtures are synthetic and verify that the parser decodes the documented
structure consistently: field offsets, little-endian, variable UTF-16LE
strings, time and plain-text derivation. Byte-exact agreement with real
hardware is verified separately in ``test_fixtures.py``.
"""

from __future__ import annotations

import struct
from datetime import datetime

from protocol import parse
from protocol.rare import parse_rare


def build_rare(
    *,
    version: int = 3,
    field2: int = 1,
    terminal: int = 0x00100042,
    serial: str = "80156809150025",
    relay: int = 2,
    user: int = 46,
    finger: int = 4,
    event: str = "",
    time: str = "20260715 143005",
    name: str = "Anna Example",
    personal: str = "1002",
) -> bytes:
    """Build a rare packet (terminal server layout)."""
    header = struct.pack(
        "<III14sBBII16s16s",
        version,
        field2,
        terminal,
        serial.encode("latin-1"),
        relay,
        0,
        user,
        finger,
        event.encode("latin-1"),
        time.encode("ascii"),
    )
    body = (
        name.encode("utf-16-le")
        + b"\x00\x00"
        + personal.encode("utf-16-le")
        + b"\x00\x00"
    )
    return header + body


def test_rare_terminal_access_granted():
    ev = parse_rare(build_rare())
    assert ev is not None
    assert ev.source_format == "rare"
    assert ev.packet_version == 3
    assert ev.serial == "80156809150025"
    assert ev.user_id == 46
    assert ev.user_name == "Anna Example"
    assert ev.personal_id == "1002"
    assert ev.finger_id == 4
    assert ev.finger_name == "Left index finger"
    assert ev.relay_id == 2
    assert ev.relay_name == "Relay 2"
    assert ev.action_code == 1
    assert ev.action_name == "Entry"
    assert ev.timestamp == datetime(2026, 7, 15, 14, 30, 5)
    assert ev.ha_event_type == "access_granted"


def test_rare_refused_unknown_finger():
    ev = parse_rare(build_rare(field2=4, user=0, finger=0, name="", personal=""))
    assert ev.action_code == 4
    assert ev.action_name == "Unknown finger"
    assert ev.user_id is None
    assert ev.user_name is None
    assert ev.finger_name == "Not defined"
    assert ev.ha_event_type == "access_denied_unknown"


def test_rare_alarm_arm():
    assert parse_rare(build_rare(field2=5)).ha_event_type == "alarm_arm"


def test_rare_rfid_identification():
    ev = parse_rare(build_rare(field2=1, finger=16))
    assert ev.finger_name == "RFID"
    assert ev.ha_event_type == "rfid"


def test_rare_v2_uses_event_id():
    ev = parse_rare(build_rare(version=5, field2=19, name="", personal=""))
    assert ev.source_format == "rare_v2"
    assert ev.event_id == 19
    assert ev.event_name == "Rejected: unknown"
    assert ev.action_code is None
    assert ev.ha_event_type == "access_denied_unknown"


def test_rare_rejects_short_and_unknown_version():
    assert parse_rare(b"\x00" * 10) is None
    assert parse_rare(build_rare(version=9)) is None


def test_dispatch_detects_rare():
    ev = parse(build_rare())
    assert ev is not None
    assert ev.source_format == "rare"
