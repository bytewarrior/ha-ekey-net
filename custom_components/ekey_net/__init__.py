"""The ekey net integration for Home Assistant.

Starts the UDP listener when the config entry is loaded and forwards each
decoded event to the entity platforms and the ``ekey_net_event`` bus event.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_BIND_ADDRESS, DEFAULT_BIND_ADDRESS, PLATFORMS
from .coordinator import EkeyNetListener

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ekey net from a config entry."""
    host = entry.options.get(CONF_BIND_ADDRESS) or DEFAULT_BIND_ADDRESS
    port = entry.data[CONF_PORT]

    listener = EkeyNetListener(hass, entry, host, port)
    try:
        await listener.async_start()
    except OSError as err:
        raise ConfigEntryNotReady(
            f"Could not open UDP port {port}: {err}"
        ) from err

    entry.runtime_data = listener
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    listener: EkeyNetListener | None = getattr(entry, "runtime_data", None)
    if listener is not None:
        await listener.async_stop()
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options (format/mapping/bind) change."""
    await hass.config_entries.async_reload(entry.entry_id)
