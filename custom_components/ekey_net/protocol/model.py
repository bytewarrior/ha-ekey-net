"""Normalized event data model and enrichment.

Pure Python layer without any Home Assistant dependency. ``enrich`` translates
the numeric raw IDs into plain text automatically and derives the HA event
type. The ``person`` field stays empty and is only populated by the HA layer
from the optional user mapping.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .tables import EVENT_ID_NAMES, FINGER_NAMES, RELAY_NAMES


@dataclass(slots=True)
class EkeyEvent:
    """An ekey net event decoded from a UDP packet."""

    source_format: str
    packet_version: int | None = None
    serial: str | None = None
    terminal_id: int | None = None
    user_id: int | None = None
    user_name: str | None = None
    personal_id: str | None = None
    finger_id: int | None = None
    finger_name: str | None = None
    relay_id: int | None = None
    relay_name: str | None = None
    action_code: int | None = None
    action_name: str | None = None
    event_id: int | None = None
    event_name: str | None = None
    event_code: str | None = None
    timestamp: datetime | None = None
    person: str | None = None  # populated by the HA person mapping
    ha_event_type: str = "other"
    raw: bytes | None = None

    def as_dict(self) -> dict[str, Any]:
        """JSON-friendly dict (without raw bytes) for bus events/diagnostics."""
        data = asdict(self)
        data.pop("raw", None)
        if self.timestamp is not None:
            data["timestamp"] = self.timestamp.isoformat()
        return data


def derive_ha_event_type(ev: EkeyEvent) -> str:
    """Derive the HA event type from the raw fields."""
    ac = ev.action_code
    if ac == 3 or ev.event_id == 20:
        return "access_denied_known"
    if ac in (4, 19) or ev.event_id == 19:
        return "access_denied_unknown"
    if ac == 20:
        return "access_denied_known"
    if ac == 5:
        return "alarm_arm"
    if ac == 6:
        return "alarm_disarm"
    if ev.finger_id == 16:
        return "rfid"
    if ev.finger_id == 13:
        return "pin"
    if ac in (1, 2):
        return "access_granted"
    return "other"


def enrich(ev: EkeyEvent) -> EkeyEvent:
    """Populate the plain-text fields from the raw IDs and the HA event type."""
    if ev.finger_id is not None:
        ev.finger_name = FINGER_NAMES.get(ev.finger_id)
    if ev.relay_id is not None:
        ev.relay_name = RELAY_NAMES.get(ev.relay_id)
    if ev.event_id is not None:
        ev.event_name = EVENT_ID_NAMES.get(ev.event_id)
    ev.ha_event_type = derive_ha_event_type(ev)
    return ev
