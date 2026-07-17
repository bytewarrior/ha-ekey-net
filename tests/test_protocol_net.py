"""Unit tests for the plain-text net/net-v2 parser."""

from __future__ import annotations

from protocol import parse
from protocol.net import parse_net


def build_net(
    *,
    pkt: str = "1",
    user: str = "000046",
    finger: str = "4",
    serial: str = "80156809150025",
    last: str = "000001",
) -> bytes:
    """Build a 28-character net/net-v2 packet."""
    text = pkt + user + finger + serial + last
    assert len(text) == 28
    return text.encode("ascii")


def test_net_enter_with_finger():
    ev = parse_net(build_net())
    assert ev is not None
    assert ev.source_format == "net"
    assert ev.user_id == 46
    assert ev.finger_id == 4
    assert ev.finger_name == "Left index finger"
    assert ev.serial == "80156809150025"
    assert ev.action_code == 1
    assert ev.action_name == "Entry"
    assert ev.ha_event_type == "access_granted"


def test_net_rfid():
    ev = parse_net(build_net(finger="@"))
    assert ev.finger_id == 16
    assert ev.finger_name == "RFID"
    assert ev.ha_event_type == "rfid"


def test_net_pin():
    ev = parse_net(build_net(finger="P"))
    assert ev.finger_id == 13
    assert ev.finger_name == "PIN code"
    assert ev.ha_event_type == "pin"


def test_net_reject_undefined_user_and_serial():
    ev = parse_net(
        build_net(user="000000", finger="-", serial="**************", last="000019")
    )
    assert ev.user_id is None
    assert ev.serial is None
    assert ev.finger_id == 0
    assert ev.finger_name == "Not defined"
    assert ev.action_code == 19
    assert ev.action_name == "Rejected"
    assert ev.ha_event_type == "access_denied_unknown"


def test_net_v2_uses_event_id():
    ev = parse_net(build_net(pkt="2", last="000019"))
    assert ev.source_format == "net_v2"
    assert ev.event_id == 19
    assert ev.event_name == "Rejected: unknown"
    assert ev.action_code is None
    assert ev.ha_event_type == "access_denied_unknown"


def test_net_finger0_is_right_little():
    assert parse_net(build_net(finger="0")).finger_name == "Right little finger"


def test_net_rejects_wrong_length():
    assert parse_net(b"123") is None
    assert parse_net(b"9" + b"0" * 27) is None


def test_dispatch_detects_net():
    ev = parse(build_net())
    assert ev is not None
    assert ev.source_format == "net"
