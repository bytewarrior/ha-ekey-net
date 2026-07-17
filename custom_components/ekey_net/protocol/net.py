"""Parser for the ekey net plain-text formats ``net`` and ``net v2``.

ANSI plain text, 28 characters (Converter LAN from firmware 2.1.11.21):

    net    : '1' + UserID(6) + Finger(1) + Serial(14) + ActionCode(6)
    net v2 : '2' + UserID(6) + Finger(1) + Serial(14) + EventID(6)
"""

from __future__ import annotations

from .model import EkeyEvent, enrich
from .tables import NET_ACTION_NAMES, NET_FINGER_FROM_CHAR

NET_LEN = 28


def _num(text: str) -> int | None:
    """Convert a numeric field to int; non-numeric -> None."""
    text = text.strip()
    return int(text) if text.isdigit() else None


def parse_net(data: bytes | str) -> EkeyEvent | None:
    """Decode a plain-text net/net-v2 packet. Returns ``None`` on mismatch."""
    if isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
        text = raw.decode("ascii", "replace")
    else:
        text = data
        raw = data.encode("ascii", "replace")

    if len(text) != NET_LEN or text[0] not in ("1", "2"):
        return None

    pkt = text[0]
    user_id = _num(text[1:7])
    finger_char = text[7]
    serial_raw = text[8:22]
    last = text[22:28]

    ev = EkeyEvent(
        source_format="net" if pkt == "1" else "net_v2",
        packet_version=int(pkt),
        serial=None if set(serial_raw) == {"*"} else serial_raw,
        user_id=None if user_id == 0 else user_id,
        finger_id=NET_FINGER_FROM_CHAR.get(finger_char),
        raw=raw,
    )

    if pkt == "1":
        ev.action_code = _num(last)
        ev.action_name = NET_ACTION_NAMES.get(ev.action_code)
    else:
        ev.event_id = _num(last)

    return enrich(ev)
