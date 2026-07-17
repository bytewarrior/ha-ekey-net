"""Device triggers: automations per ekey event type and fingerprint scanner.

Provides triggers such as "Access granted" or "Access denied (unknown)" per
fingerprint scanner device in the automation editor. Implemented via the
``ekey_net_event`` bus event (filtered by serial number and event type).
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import ATTR_SERIAL, DOMAIN, EVENT_EKEY_NET, EVENT_TYPES
from .helpers import serial_from_identifier

# "other" makes little sense as a trigger and is hidden.
TRIGGER_TYPES: tuple[str, ...] = tuple(t for t in EVENT_TYPES if t != "other")

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES)}
)


def _serial_for_device(hass: HomeAssistant, device_id: str) -> str | None:
    device = dr.async_get(hass).async_get(device_id)
    if device is None:
        return None
    if device.serial_number:
        return device.serial_number
    for domain, ident in device.identifiers:
        if domain == DOMAIN:
            return serial_from_identifier(ident)
    return None


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List the available triggers of a fingerprint scanner device."""
    return [
        {
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: trigger_type,
        }
        for trigger_type in TRIGGER_TYPES
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a device trigger to the ``ekey_net_event`` bus event."""
    serial = _serial_for_device(hass, config[CONF_DEVICE_ID])
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: EVENT_EKEY_NET,
            event_trigger.CONF_EVENT_DATA: {
                # Keys match EkeyEvent.as_dict() (bus event payload).
                ATTR_SERIAL: serial,
                "ha_event_type": config[CONF_TYPE],
            },
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
