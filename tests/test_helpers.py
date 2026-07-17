"""Unit tests for the HA-free helper functions."""

from __future__ import annotations

from helpers import parse_id_map, serial_from_identifier


def test_parse_id_map_basic():
    assert parse_id_map("46 = person.anna\n47=person.bob") == {
        46: "person.anna",
        47: "person.bob",
    }


def test_parse_id_map_colon_and_comments():
    text = "# comment\n3: person.c\n\n   \n4 : person.d"
    assert parse_id_map(text) == {3: "person.c", 4: "person.d"}


def test_parse_id_map_skips_invalid_lines():
    assert parse_id_map("x=person.x\n5=\n=leer\n6=person.f") == {6: "person.f"}


def test_parse_id_map_empty_input():
    assert parse_id_map("") == {}
    assert parse_id_map(None) == {}


def test_serial_from_identifier():
    assert serial_from_identifier("01HXYZ_80290510220655") == "80290510220655"
    assert serial_from_identifier("abc123_unknown") == "unknown"
