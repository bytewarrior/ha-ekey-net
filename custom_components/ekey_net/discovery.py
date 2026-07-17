"""Shared dynamic entity creation per fingerprint scanner (+ startup restore).

Both platforms (``event``, ``sensor``) create their entities per fingerprint
scanner (identified by serial number) dynamically: known scanners are restored
from the device registry at startup, new ones are created on the first packet.
The concrete entity type is supplied by a factory.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, MANUFACTURER, SIGNAL_EKEY_EVENT, UNKNOWN_SERIAL
from .helpers import serial_from_identifier
from .protocol.model import EkeyEvent

#: Factory: (entry, serial) -> list of new entities (with ``set_pending``).
EntityFactory = Callable[[ConfigEntry, str], list[Any]]


def build_device_info(entry: ConfigEntry, serial: str) -> DeviceInfo:
    """Uniform device info per fingerprint scanner (shared by event and sensor entities)."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_{serial}")},
        manufacturer=MANUFACTURER,
        model="ekey net fingerprint scanner",
        name=f"ekey fingerprint scanner {serial}",
        serial_number=None if serial == UNKNOWN_SERIAL else serial,
    )


@callback
def async_setup_scanner_discovery(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    factory: EntityFactory,
) -> None:
    """Set up restore + dynamic creation of a platform's entities."""
    known: set[str] = set()

    # Restore already known scanners from the device registry.
    dev_reg = dr.async_get(hass)
    restored: list[Any] = []
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        for domain, ident in device.identifiers:
            if domain != DOMAIN:
                continue
            serial = serial_from_identifier(ident)
            if serial not in known:
                known.add(serial)
                restored.extend(factory(entry, serial))
    if restored:
        async_add_entities(restored)

    @callback
    def _discover(event: EkeyEvent) -> None:
        serial = event.serial or UNKNOWN_SERIAL
        if serial in known:
            return  # already present - the entity handles the event itself
        known.add(serial)
        entities = factory(entry, serial)
        for entity in entities:
            entity.set_pending(event)
        async_add_entities(entities)

    entry.async_on_unload(
        async_dispatcher_connect(
            hass, SIGNAL_EKEY_EVENT.format(entry.entry_id), _discover
        )
    )
