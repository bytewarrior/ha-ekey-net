"""Pure, Home Assistant-free protocol layer of the ekey net integration.

Decodes incoming UDP datagrams into a normalized :class:`EkeyEvent`. Fully free
of any ``homeassistant`` import so the parsers can be tested independently of
hardware and of an installed Home Assistant.
"""

from __future__ import annotations

from collections.abc import Callable

from .model import EkeyEvent
from .net import NET_LEN, parse_net
from .rare import HEADER_LEN, parse_rare

__all__ = ["EkeyEvent", "get_parser", "parse", "parse_net", "parse_rare"]

type PacketParser = Callable[[bytes], EkeyEvent | None]


def parse(data: bytes) -> EkeyEvent | None:
    """Auto-detect the format and decode the packet.

    Order: first the compact plain-text ``net`` format (28 bytes, starts with
    ``'1'``/``'2'``), then the binary ``rare`` format (version field).
    """
    if not data:
        return None
    if len(data) == NET_LEN and data[:1] in (b"1", b"2"):
        event = parse_net(data)
        if event is not None:
            return event
    if len(data) >= HEADER_LEN:
        return parse_rare(data)
    return None


def get_parser(fmt: str | None) -> PacketParser:
    """Return the parser function for a forced format (``None``/``auto`` -> parse)."""
    if fmt in ("rare", "rare_v2"):
        return parse_rare
    if fmt in ("net", "net_v2"):
        return parse_net
    return parse
