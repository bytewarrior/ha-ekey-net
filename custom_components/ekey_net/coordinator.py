"""UDP listener and event dispatch of the ekey net integration (HA layer).

Binds the configured UDP port, decodes incoming packets via the HA-free
protocol layer and distributes each event in two ways:

* via a dispatcher signal to the connected event entities,
* as the Home Assistant bus event ``ekey_net_event`` - making events visible in
  *Developer Tools -> Events* and usable as automation triggers.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_NAME_MAP,
    CONF_PROTOCOL_FORMAT,
    CONF_USER_MAP,
    EVENT_EKEY_NET,
    PROTOCOL_AUTO,
    SIGNAL_EKEY_EVENT,
)
from .helpers import parse_id_map
from .protocol import get_parser
from .protocol.model import EkeyEvent
from .protocol.receiver import EkeyDatagramProtocol

_LOGGER = logging.getLogger(__name__)


class EkeyNetListener:
    """Binds a UDP port, parses packets and distributes events into HA."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, host: str, port: int
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.host = host
        self.port = port
        options = entry.options
        self._parser = get_parser(options.get(CONF_PROTOCOL_FORMAT, PROTOCOL_AUTO))
        self._user_map = parse_id_map(options.get(CONF_USER_MAP))
        self._name_map = parse_id_map(options.get(CONF_NAME_MAP))
        self._transport = None
        #: Ring buffer of the most recent events (for diagnostics).
        self.recent_events: deque[dict[str, Any]] = deque(maxlen=20)

    @property
    def running(self) -> bool:
        """True while the UDP endpoint is open."""
        return self._transport is not None

    async def async_start(self) -> None:
        """Open the UDP endpoint. Raises OSError if the port is in use."""
        transport, _ = await self.hass.loop.create_datagram_endpoint(
            lambda: EkeyDatagramProtocol(self._handle_event, self._parser),
            local_addr=(self.host, self.port),
        )
        self._transport = transport
        _LOGGER.info("ekey net: UDP listener active on %s:%s", self.host, self.port)

    async def async_stop(self) -> None:
        """Close the UDP endpoint."""
        if self._transport is not None:
            self._transport.close()
            self._transport = None
            _LOGGER.debug("ekey net: UDP listener stopped")

    @callback
    def _handle_event(self, event: EkeyEvent) -> None:
        """Enrich an event (mapping) and distribute it into HA."""
        if event.user_id is not None:
            if self._user_map:
                event.person = self._user_map.get(event.user_id)
            if event.user_name is None and self._name_map:
                event.user_name = self._name_map.get(event.user_id)

        _LOGGER.debug("ekey net event received: %s", event)
        payload = event.as_dict()
        self.recent_events.append(payload)
        async_dispatcher_send(
            self.hass, SIGNAL_EKEY_EVENT.format(self.entry.entry_id), event
        )
        self.hass.bus.async_fire(EVENT_EKEY_NET, payload)
