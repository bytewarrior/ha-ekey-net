"""Home Assistant-free asyncio UDP receiver for ekey net packets.

A plain :class:`asyncio.DatagramProtocol`: decodes incoming datagrams and calls
a callback for every recognized event. Free of any ``homeassistant`` import so
UDP reception can be tested with plain asyncio (without HA and without hardware).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from . import parse
from .model import EkeyEvent

_LOGGER = logging.getLogger(__name__)

type EventCallback = Callable[[EkeyEvent], None]
type PacketParser = Callable[[bytes], EkeyEvent | None]


class EkeyDatagramProtocol(asyncio.DatagramProtocol):
    """Receives UDP datagrams, parses them and reports events via callback."""

    def __init__(self, on_event: EventCallback, parser: PacketParser = parse) -> None:
        self._on_event = on_event
        self._parser = parser
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            event = self._parser(bytes(data))
        except Exception:  # pragma: no cover - guard against unexpected parser errors
            _LOGGER.exception("Error parsing an ekey UDP packet from %s", addr)
            return
        if event is None:
            _LOGGER.debug(
                "Uninterpretable UDP packet (%d bytes) from %s", len(data), addr
            )
            return
        self._on_event(event)

    def error_received(self, exc: Exception) -> None:
        _LOGGER.debug("UDP error received: %s", exc)
