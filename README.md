# ekey net for Home Assistant

A custom integration that makes **all events of an ekey net system** usable in
Home Assistant — as an `event` entity per fingerprint scanner, with automatic
translation of the raw IDs into plain text (finger, action, relay) and an
optional mapping of ekey users to Home Assistant persons.

The integration listens for the **UDP event transmission** of an ekey net
system (terminal server or CV LAN) and turns every access event into a native
Home Assistant event that can be used in automations, dashboards and the
logbook.

> **Target system:** ekey **net** (Ethernet, Windows server system).
> This integration is **not** for ekey home/multi or the ekey bionyx cloud
> product — see [Scope](#scope-vs-other-ekey-integrations).

## Features

- **Local push, no polling** — events arrive the moment they happen.
- **Zero-config device creation** — a device and entities are created
  automatically per fingerprint scanner as soon as the first packet arrives.
- **Automatic plain-text enrichment** — numeric IDs are translated
  automatically: finger ID → finger name, action code → action, relay ID →
  relay. The raw IDs are kept as attributes as well.
- **Device triggers** for comfortable automations (`Access granted`,
  `Access denied (unknown finger)`, `RFID identification`, …).
- **Convenience sensors** per scanner (`Last user`, `Last finger`,
  `Last action`).
- **Optional user mapping** — link an ekey user to a Home Assistant `person`
  and/or a display name.
- **Diagnostics** with the most recent events (clear names redacted).
- **Auto-detection** of the packet format (`rare` / `net`), with a manual
  override in the options.

## Requirements

- Home Assistant **2024.11.0** or newer.
- An ekey **net** system whose terminal server / CV LAN can send UDP event
  packets to the Home Assistant host.

## Installation

### HACS (custom repository)

1. In HACS, add this repository (`https://github.com/bytewarrior/ha-ekey-net`)
   as a custom repository of type *Integration*.
2. Install **ekey net** and restart Home Assistant.

### Manual

Copy the `custom_components/ekey_net` folder into your Home Assistant
`config/custom_components/` directory and restart Home Assistant.

## Configuration

### 1. On the ekey net side

In **ekey net admin**, configure a **UDP packet recipient**:

- **IP address:** the IP of your Home Assistant host.
- **Port:** the port you will enter in Home Assistant (default `56000`).

Then run **"Send changes to devices"** so the terminal server starts sending
event packets. The **terminal server `rare` format** is recommended because it
already contains the resolved user name.

### 2. On the Home Assistant side

1. Go to **Settings → Devices & Services → Add Integration** and search for
   **ekey net**.
2. Enter the **UDP port** (default `56000`). That is all that is required —
   scanners and entities are created automatically once the first event
   arrives.

### Options

Open the integration's **Configure** dialog to fine-tune:

- **Protocol format** — `auto` (default) detects `rare`/`net` automatically;
  you can force a specific format.
- **User → person mapping** — one mapping per line, e.g. `46 = person.anna`.
  Adds the linked `person` to each event of that user.
- **User → display name** — fallback display name per user ID, e.g. `46 = Anna`
  (used when the packet carries no name).
- **Bind address** — leave empty to listen on all interfaces (`0.0.0.0`).

Saving the options reloads the integration.

## Events and attributes

Each fingerprint scanner gets an `event` entity that fires on every access
event. The event carries these attributes (raw IDs **and** enriched plain
text):

| Attribute | Description |
|-----------|-------------|
| `user_id` / `user_name` / `person` | ekey user ID, resolved name, mapped HA person |
| `finger_id` / `finger` | finger ID and its plain-text name |
| `action_code` / `action` | action code and its plain-text name |
| `relay_id` / `relay` | relay ID and its plain-text name |
| `serial` / `terminal_id` | scanner serial and terminal ID |
| `event_id` / `event_code` | event ID / raw event code (rare v2 / net v2) |

The event **type** is one of: `access_granted`, `access_denied_unknown`,
`access_denied_known`, `rfid`, `pin`, `digital_input`, `alarm_arm`,
`alarm_disarm`, `other`.

Every event is also fired on the Home Assistant event bus as `ekey_net_event`,
which is visible under **Developer Tools → Events** and usable as an automation
trigger.

## Automations

The integration provides **device triggers** per scanner (e.g. *Access
granted*, *Access denied (unknown finger)*), so you can build automations
directly in the UI without touching YAML.

## Protocol

The supported UDP formats (`rare`, `rare v2`, `net`, `net v2`) are described in
[docs/PROTOCOL.md](docs/PROTOCOL.md).

## Scope vs. other ekey integrations

- **`ekeybionyx`** (in HA Core) is for the **ekey bionyx cloud product** — not
  usable for ekey net.
- `ha-ekeylegacy` and `ekey_home_rs485` target **ekey home/multi** (small
  standalone systems), not the net system.
- This integration fills the gap for **ekey net**.

## Development

The protocol layer (`custom_components/ekey_net/protocol/`) is deliberately free
of any Home Assistant dependency, so the parsers can be tested without an
installed Home Assistant or any hardware:

```bash
pytest
```

The tests cover the binary `rare`/`rare v2` parser, the plain-text `net`/`net
v2` parser, the pure asyncio UDP receiver and the helper functions, plus byte
verification against anonymized real-capture fixtures.

## License

Released under the [MIT License](LICENSE).
