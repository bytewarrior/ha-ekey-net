"""Pure helper functions of the ekey net integration (no HA dependency)."""

from __future__ import annotations


def serial_from_identifier(identifier: str) -> str:
    """Extract the fingerprint scanner serial number from a device identifier.

    Device identifiers have the form ``<entry_id>_<serial>`` (see
    ``event.py``/``sensor.py``). Serial numbers are purely numeric (or
    ``unknown``) and contain no underscores.
    """
    return identifier.rsplit("_", 1)[-1]


def parse_id_map(text: str | None) -> dict[int, str]:
    """Parse a multi-line ``ekey user ID = value`` mapping into a dict.

    - Separator ``=`` or ``:``.
    - Empty lines and ``#`` comments are ignored.
    - Lines with a non-numeric ID or an empty value are skipped.

    Example::

        "46 = person.anna\\n47 = person.bob"  ->  {46: "person.anna", 47: "person.bob"}
    """
    result: dict[int, str] = {}
    if not text:
        return result
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
        elif ":" in line:
            key, _, value = line.partition(":")
        else:
            continue
        key = key.strip()
        value = value.strip()
        if key.isdigit() and value:
            result[int(key)] = value
    return result
