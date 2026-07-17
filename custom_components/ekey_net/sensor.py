"""sensor platform of the ekey net integration (convenience/dashboards).

A few "last ..." sensors per fingerprint scanner, updated on every event.
Creation/restore via the shared ``discovery`` logic.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SIGNAL_EKEY_EVENT, UNKNOWN_SERIAL
from .discovery import async_setup_scanner_discovery, build_device_info
from .protocol.model import EkeyEvent


@dataclass(frozen=True, kw_only=True)
class EkeySensorDescription(SensorEntityDescription):
    """Sensor description with value derivation from an EkeyEvent."""

    value_fn: Callable[[EkeyEvent], str | int | None]


def _last_user(event: EkeyEvent) -> str | int | None:
    if event.user_name:
        return event.user_name
    return event.user_id


SENSOR_DESCRIPTIONS: tuple[EkeySensorDescription, ...] = (
    EkeySensorDescription(
        key="last_user",
        translation_key="last_user",
        icon="mdi:account",
        value_fn=_last_user,
    ),
    EkeySensorDescription(
        key="last_finger",
        translation_key="last_finger",
        icon="mdi:fingerprint",
        value_fn=lambda event: event.finger_name,
    ),
    EkeySensorDescription(
        key="last_action",
        translation_key="last_action",
        icon="mdi:gesture-tap",
        value_fn=lambda event: event.action_name or event.event_name or event.ha_event_type,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the dynamic creation of the sensors per fingerprint scanner."""
    async_setup_scanner_discovery(
        hass,
        entry,
        async_add_entities,
        lambda cfg, serial: [
            EkeyLastValueSensor(cfg, serial, desc) for desc in SENSOR_DESCRIPTIONS
        ],
    )


class EkeyLastValueSensor(SensorEntity):
    """Shows a value from the most recently received event of a scanner."""

    _attr_has_entity_name = True
    entity_description: EkeySensorDescription

    def __init__(
        self, entry: ConfigEntry, serial: str, description: EkeySensorDescription
    ) -> None:
        self.entity_description = description
        self._entry = entry
        self._serial = serial
        self._pending: EkeyEvent | None = None
        self._attr_unique_id = f"{entry.entry_id}_{serial}_{description.key}"
        self._attr_device_info = build_device_info(entry, serial)

    @callback
    def set_pending(self, event: EkeyEvent) -> None:
        self._pending = event

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_EKEY_EVENT.format(self._entry.entry_id),
                self._handle_signal,
            )
        )
        if self._pending is not None:
            self._apply(self._pending)
            self._pending = None

    @callback
    def _handle_signal(self, event: EkeyEvent) -> None:
        if (event.serial or UNKNOWN_SERIAL) == self._serial:
            self._apply(event)

    @callback
    def _apply(self, event: EkeyEvent) -> None:
        self._attr_native_value = self.entity_description.value_fn(event)
        self.async_write_ha_state()
