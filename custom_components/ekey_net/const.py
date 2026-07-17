"""Constants of the ekey net integration (Home Assistant layer).

The static mapping tables (finger, action, relay, event names and event types)
live Home Assistant-free in :mod:`.protocol.tables` and are only re-exported
here (single source of truth).
"""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

# Re-export the pure mapping tables for the HA layer.
from .protocol.tables import (  # noqa: F401
    ACTION_NAMES,
    EVENT_ID_NAMES,
    EVENT_TYPES,
    FINGER_NAMES,
    RELAY_NAMES,
)

# --- Base ---------------------------------------------------------------------

DOMAIN: Final = "ekey_net"
DEFAULT_NAME: Final = "ekey net"
MANUFACTURER: Final = "ekey biometric systems"

#: Placeholder serial when a packet carries no fingerprint scanner serial number.
UNKNOWN_SERIAL: Final = "unknown"

#: Default receive port for the ekey UDP transmission (ekey factory setting).
DEFAULT_PORT: Final = 56000

#: Default bind address of the UDP listener (all interfaces).
DEFAULT_BIND_ADDRESS: Final = "0.0.0.0"

#: Platforms loaded by the config entry.
PLATFORMS: Final[list[Platform]] = [Platform.EVENT, Platform.SENSOR]

# --- Event bus / dispatcher ---------------------------------------------------

#: Home Assistant bus event fired for every ekey event.
EVENT_EKEY_NET: Final = "ekey_net_event"
#: Dispatcher signal per config entry (format with ``entry_id``).
SIGNAL_EKEY_EVENT: Final = "ekey_net_event_{}"

# --- Configuration keys (config/options flow) ---------------------------------

CONF_BIND_ADDRESS: Final = "bind_address"
CONF_PROTOCOL_FORMAT: Final = "protocol_format"
CONF_USER_MAP: Final = "user_map"          # ekey user ID -> HA person entity_id
CONF_NAME_MAP: Final = "name_map"          # ekey user ID -> display name (fallback)

PROTOCOL_AUTO: Final = "auto"
PROTOCOL_RARE: Final = "rare"
PROTOCOL_RARE_V2: Final = "rare_v2"
PROTOCOL_NET: Final = "net"
PROTOCOL_NET_V2: Final = "net_v2"
PROTOCOL_FORMATS: Final = (
    PROTOCOL_AUTO,
    PROTOCOL_RARE,
    PROTOCOL_RARE_V2,
    PROTOCOL_NET,
    PROTOCOL_NET_V2,
)

# --- Event attributes (extra_data of the event entity) ------------------------

ATTR_USER_ID: Final = "user_id"
ATTR_USER_NAME: Final = "user_name"
ATTR_PERSON: Final = "person"
ATTR_FINGER_ID: Final = "finger_id"
ATTR_FINGER: Final = "finger"
ATTR_ACTION: Final = "action"
ATTR_ACTION_CODE: Final = "action_code"
ATTR_RELAY: Final = "relay"
ATTR_RELAY_ID: Final = "relay_id"
ATTR_SERIAL: Final = "serial"
ATTR_TERMINAL_ID: Final = "terminal_id"
ATTR_EVENT_CODE: Final = "event_code"
ATTR_EVENT_ID: Final = "event_id"
