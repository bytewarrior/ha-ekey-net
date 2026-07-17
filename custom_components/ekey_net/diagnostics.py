"""Diagnostics data for an ekey net config entry.

Provides configuration, listener status and the most recently received events.
Clear names/persons are redacted (privacy).
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import ATTR_PERSON, ATTR_USER_NAME, CONF_NAME_MAP, CONF_USER_MAP
from .coordinator import EkeyNetListener

TO_REDACT_OPTIONS = {CONF_USER_MAP, CONF_NAME_MAP}
TO_REDACT_EVENT = {ATTR_USER_NAME, ATTR_PERSON, "personal_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    listener: EkeyNetListener | None = getattr(entry, "runtime_data", None)
    recent = list(listener.recent_events) if listener is not None else []

    return {
        "entry": {
            "data": dict(entry.data),
            "options": async_redact_data(dict(entry.options), TO_REDACT_OPTIONS),
        },
        "listener": {
            "host": listener.host if listener else None,
            "port": listener.port if listener else None,
            "running": listener.running if listener else False,
        },
        "recent_events": [async_redact_data(event, TO_REDACT_EVENT) for event in recent],
    }
