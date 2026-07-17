"""Pure (Home Assistant-free) mapping tables for the ekey net protocols.

Single source of truth for the ID-to-plain-text translation. Deliberately kept
free of any ``homeassistant`` dependency so the parsers and their tests run
without an installed Home Assistant. ``const.py`` re-exports these tables for
the HA layer.
"""

from __future__ import annotations

from typing import Final

#: Finger ID (rare format, uint32) -> plain text.
FINGER_NAMES: Final[dict[int, str]] = {
    0: "Not defined",
    1: "Left little finger",
    2: "Left ring finger",
    3: "Left middle finger",
    4: "Left index finger",
    5: "Left thumb",
    6: "Right thumb",
    7: "Right index finger",
    8: "Right middle finger",
    9: "Right ring finger",
    10: "Right little finger",
    13: "PIN code",
    16: "RFID",
}

#: Terminal server action code (rare format) -> plain text.
ACTION_NAMES: Final[dict[int, str]] = {
    0: "No action code",
    1: "Entry",
    2: "Exit",
    3: "Rejected (known)",
    4: "Unknown finger",
    5: "Alarm system armed",
    6: "Alarm system disarmed",
    15: "Device restart",
}

#: Relay ID -> plain text.
RELAY_NAMES: Final[dict[int, str]] = {
    0: "Not defined",
    1: "Relay 1",
    2: "Relay 2",
    3: "Relay 3",
    4: "Relay 4",
}

#: Predefined event IDs -> plain text (for rare_v2/net_v2).
EVENT_ID_NAMES: Final[dict[int, str]] = {
    1: "Switch relay 1 with day schedule",
    2: "Relay 1 permanently on with day schedule",
    3: "Relay 1 permanently off",
    4: "Relay 2 permanently on with day schedule, LED on",
    5: "Relay 2 permanently off, LED off",
    6: "Relay 3 permanently on",
    7: "Relay 4 permanently on",
    8: "Switch relay 2",
    9: "Switch relay 3",
    10: "Switch relay 4",
    15: "Toggle relay 1",
    16: "Toggle relay 2",
    17: "Toggle relay 3",
    18: "Toggle relay 4",
    19: "Rejected: unknown",
    20: "Rejected: known",
    21: "Switch local relay 1 with day schedule",
    23: "Local relay 1 permanently on with day schedule",
    24: "Local relay 1 permanently off",
    25: "Toggle local relay 1",
    54: "Relay 3 permanently off",
    55: "Relay 4 permanently off",
    56: "Switch relay 1 with day schedule",
    57: "Switch relay 2 with day schedule",
    58: "Switch relay 3 with day schedule",
    59: "Switch relay 4 with day schedule",
}

#: Finger character in the plain-text ``net`` format -> finger ID (rare semantics).
NET_FINGER_FROM_CHAR: Final[dict[str, int]] = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "0": 10,
    "-": 0,
    "P": 13,
    "@": 16,
}

#: Action code in the plain-text ``net`` format -> plain text (0/1/19).
NET_ACTION_NAMES: Final[dict[int, str]] = {
    0: "No action code",
    1: "Entry",
    19: "Rejected",
}

#: HA event types of the event entity.
EVENT_TYPES: Final[list[str]] = [
    "access_granted",
    "access_denied_unknown",
    "access_denied_known",
    "rfid",
    "pin",
    "digital_input",
    "alarm_arm",
    "alarm_disarm",
    "other",
]
