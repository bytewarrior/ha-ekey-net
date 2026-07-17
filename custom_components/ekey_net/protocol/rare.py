"""Parser for the binary ekey net ``rare`` formats (rare, rare v2).

Little-endian (x86). Fixed part = 68 bytes, followed by two null-terminated
UTF-16LE strings (name, personal ID) - only actually populated by the terminal
server ``rare`` variant.
"""

from __future__ import annotations

import struct
from datetime import datetime

from .model import EkeyEvent, enrich
from .tables import ACTION_NAMES

# Version(4) Field2(4) TerminalID(4) Serial(14) Relay(1) Reserved(1)
# UserID(4) FingerID(4) Event(16) Time(16) = 68 bytes
_HEADER = struct.Struct("<III14sBBII16s16s")
HEADER_LEN = _HEADER.size  # 68

#: Known packet versions: 3 = rare, 4 = rare (custom), 5 = rare v2.
RARE_VERSIONS = (3, 4, 5)


def _decode_ansi(raw: bytes) -> str:
    """Decode an ANSI field up to the first null byte."""
    return raw.split(b"\x00", 1)[0].decode("latin-1", "replace").strip()


def _read_utf16z(data: bytes, offset: int) -> tuple[str, int]:
    """Read a null-terminated UTF-16LE string starting at ``offset``.

    Returns (text, offset past the terminator).
    """
    end = offset
    while end + 1 < len(data):
        if data[end] == 0 and data[end + 1] == 0:
            break
        end += 2
    text = data[offset:end].decode("utf-16-le", "replace")
    return text, end + 2


def _parse_time(raw: bytes) -> datetime | None:
    """Parse the time field of the form ``yyyymmdd hhmmss``."""
    text = raw.split(b"\x00", 1)[0].decode("ascii", "replace").strip()
    try:
        return datetime.strptime(text, "%Y%m%d %H%M%S")
    except ValueError:
        return None


def parse_rare(data: bytes) -> EkeyEvent | None:
    """Decode a binary rare/rare-v2 packet. Returns ``None`` on mismatch."""
    if len(data) < HEADER_LEN:
        return None

    (
        version,
        field2,
        terminal_id,
        serial_raw,
        relay_id,
        _reserved,
        user_id,
        finger_id,
        event_raw,
        time_raw,
    ) = _HEADER.unpack_from(data, 0)

    if version not in RARE_VERSIONS:
        return None

    ev = EkeyEvent(
        source_format="rare_v2" if version == 5 else "rare",
        packet_version=version,
        serial=_decode_ansi(serial_raw) or None,
        terminal_id=terminal_id or None,
        user_id=user_id or None,
        finger_id=finger_id,
        relay_id=relay_id,
        event_code=_decode_ansi(event_raw) or None,
        timestamp=_parse_time(time_raw),
        raw=bytes(data),
    )

    # Variable UTF-16LE strings (only the terminal server rare variant carries
    # real values).
    offset = HEADER_LEN
    if offset < len(data):
        ev.user_name, offset = _read_utf16z(data, offset)
        ev.user_name = ev.user_name or None
    if offset < len(data):
        ev.personal_id, offset = _read_utf16z(data, offset)
        ev.personal_id = ev.personal_id or None

    if version == 5:
        # rare v2: field 2 is the event ID.
        ev.event_id = field2 or None
    else:
        # rare / rare (custom): field 2 is the action code, resp. the event ID
        # of the triggering event (CV LAN).
        ev.action_code = field2
        ev.action_name = ACTION_NAMES.get(field2)

    return enrich(ev)
