# ekey net UDP protocol reference

This document describes the UDP event formats decoded by the integration. An
ekey net system (terminal server or CV LAN) sends one UDP datagram per access
event. The integration decodes each datagram into a normalized event.

Four formats are supported. The format is auto-detected, but it can also be
forced in the integration options.

| Format | Encoding | Contents |
|--------|----------|----------|
| `rare` | binary | Full event, incl. resolved user name (terminal server) |
| `rare v2` | binary | Like `rare`, but with a numeric event ID |
| `net` | plain text | Compact 28-character event, action code |
| `net v2` | plain text | Compact 28-character event, event ID |

The **terminal server `rare`** format is recommended because it carries the
resolved user name in the packet.

## `rare` / `rare v2` (binary)

Little-endian (x86). A fixed 68-byte header, optionally followed by two
null-terminated UTF-16LE strings (user name and personal ID). The trailing
strings are only populated by the terminal server variant.

### Fixed header (68 bytes)

| Offset | Size | Field | Notes |
|-------:|-----:|-------|-------|
| 0 | 4 | Version | `3` = rare, `4` = rare (custom), `5` = rare v2 |
| 4 | 4 | Field 2 | Action code (`rare`) or event ID (`rare v2`) |
| 8 | 4 | Terminal ID | Internal ID / RS-485 address |
| 12 | 14 | Serial | 14-digit fingerprint scanner serial (ANSI) |
| 26 | 1 | Relay | Relay ID |
| 27 | 1 | Reserved | |
| 28 | 4 | User ID | |
| 32 | 4 | Finger ID | |
| 36 | 16 | Event | Free-form event code (ANSI) |
| 52 | 16 | Time | ASCII, `yyyymmdd hhmmss` |

### Trailing strings (terminal server only)

Starting at offset 68, two null-terminated UTF-16LE strings follow:

1. User name
2. Personal ID

If the time field cannot be parsed, the integration falls back to the receive
time.

## `net` / `net v2` (plain text)

ANSI plain text, exactly 28 characters (Converter LAN from firmware
2.1.11.21).

```
net    : '1' + UserID(6) + Finger(1) + Serial(14) + ActionCode(6)
net v2 : '2' + UserID(6) + Finger(1) + Serial(14) + EventID(6)
```

- A user ID of `000000` and a serial consisting only of `*` mean "not present".
- The single finger character maps to the same finger IDs as the binary format.

### Finger characters

| Char | Finger |
|------|--------|
| `1`–`9` | left little … right ring finger (rare finger IDs 1–9) |
| `0` | right little finger (finger ID 10) |
| `-` | not defined (finger ID 0) |
| `P` | PIN code (finger ID 13) |
| `@` | RFID (finger ID 16) |

## ID mappings

The numeric IDs are translated into plain text using the tables in
[`custom_components/ekey_net/protocol/tables.py`](../custom_components/ekey_net/protocol/tables.py):
finger names, action names, relay names and predefined event IDs.

## Derived Home Assistant event type

The integration derives a Home Assistant event type from the raw fields:

| Condition | Event type |
|-----------|------------|
| Action code `1`/`2` (entry/exit) | `access_granted` |
| Action code `3`, or event ID `20` | `access_denied_known` |
| Action code `4`/`19`, or event ID `19` | `access_denied_unknown` |
| Action code `5` | `alarm_arm` |
| Action code `6` | `alarm_disarm` |
| Finger ID `16` | `rfid` |
| Finger ID `13` | `pin` |
| otherwise | `other` |

## Verification

The byte offsets are verified against anonymized real-capture fixtures in
[`tests/test_fixtures.py`](../tests/test_fixtures.py). The remaining unit tests
use synthetic packets encoded to the layouts above.
