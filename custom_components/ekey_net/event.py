"""event platform of the ekey net integration.

Creates one :class:`EventEntity` dynamically per fingerprint scanner (see
``discovery.py``: restore at startup + creation on the first packet). Each
entity consumes the dispatcher signal from the coordinator and fires a HA event
with the enriched attributes (finger name, person, action, relay).
"""

from __future__ import annotations

import logging

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ATTR_ACTION,
    ATTR_ACTION_CODE,
    ATTR_EVENT_CODE,
    ATTR_EVENT_ID,
    ATTR_FINGER,
    ATTR_FINGER_ID,
    ATTR_PERSON,
    ATTR_RELAY,
    ATTR_RELAY_ID,
    ATTR_SERIAL,
    ATTR_TERMINAL_ID,
    ATTR_USER_ID,
    ATTR_USER_NAME,
    EVENT_TYPES,
    SIGNAL_EKEY_EVENT,
    UNKNOWN_SERIAL,
)
from .discovery import async_setup_scanner_discovery, build_device_info
from .protocol.model import EkeyEvent

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the dynamic creation of event entities per fingerprint scanner."""
    async_setup_scanner_discovery(
        hass,
        entry,
        async_add_entities,
        lambda cfg, serial: [EkeyScannerEvent(cfg, serial)],
    )


class EkeyScannerEvent(EventEntity):
    """An event channel for exactly one ekey fingerprint scanner."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = "mdi:fingerprint"
    _attr_event_types = EVENT_TYPES

    def __init__(self, entry: ConfigEntry, serial: str) -> None:
        self._entry = entry
        self._serial = serial
        self._pending: EkeyEvent | None = None
        self._attr_unique_id = f"{entry.entry_id}_{serial}"
        self._attr_device_info = build_device_info(entry, serial)

    @callback
    def set_pending(self, event: EkeyEvent) -> None:
        """Remember the triggering event that created the entity."""
        self._pending = event

    async def async_added_to_hass(self) -> None:
        """Subscribe to further events and replay the triggering one."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_EKEY_EVENT.format(self._entry.entry_id),
                self._handle_signal,
            )
        )
        if self._pending is not None:
            self._fire(self._pending)
            self._pending = None

    @callback
    def _handle_signal(self, event: EkeyEvent) -> None:
        if (event.serial or UNKNOWN_SERIAL) == self._serial:
            self._fire(event)

    @callback
    def _fire(self, event: EkeyEvent) -> None:
        self._trigger_event(
            event.ha_event_type,
            {
                ATTR_USER_ID: event.user_id,
                ATTR_USER_NAME: event.user_name,
                ATTR_PERSON: event.person,
                ATTR_FINGER_ID: event.finger_id,
                ATTR_FINGER: event.finger_name,
                ATTR_ACTION: event.action_name,
                ATTR_ACTION_CODE: event.action_code,
                ATTR_RELAY: event.relay_name,
                ATTR_RELAY_ID: event.relay_id,
                ATTR_SERIAL: event.serial,
                ATTR_TERMINAL_ID: event.terminal_id,
                ATTR_EVENT_CODE: event.event_code,
                ATTR_EVENT_ID: event.event_id,
            },
        )
        self.async_write_ha_state()
