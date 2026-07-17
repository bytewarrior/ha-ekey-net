"""Integration test of the HA-free UDP receiver over real asyncio UDP.

Sends a synthetic packet via localhost UDP to the receiver and checks that the
callback is called with the correctly decoded event - without Home Assistant
and without hardware.
"""

from __future__ import annotations

import asyncio
import sys

import pytest

from protocol.receiver import EkeyDatagramProtocol


def _run(coro):
    """Run a coroutine in a selector loop (UDP-robust on Windows too)."""
    loop = asyncio.SelectorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _receive_one(packet: bytes):
    received: list = []
    done = asyncio.Event()

    def on_event(event) -> None:
        received.append(event)
        done.set()

    loop = asyncio.get_running_loop()
    recv_transport, _ = await loop.create_datagram_endpoint(
        lambda: EkeyDatagramProtocol(on_event),
        local_addr=("127.0.0.1", 0),
    )
    try:
        port = recv_transport.get_extra_info("sockname")[1]
        send_transport, _ = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            remote_addr=("127.0.0.1", port),
        )
        try:
            send_transport.sendto(packet)
            await asyncio.wait_for(done.wait(), timeout=2.0)
        finally:
            send_transport.close()
    finally:
        recv_transport.close()
    return received[0]


def test_receiver_decodes_net_packet():
    packet = ("1" + "000046" + "4" + "80156809150025" + "000001").encode("ascii")
    event = _run(_receive_one(packet))
    assert event.source_format == "net"
    assert event.user_id == 46
    assert event.finger_name == "Left index finger"
    assert event.ha_event_type == "access_granted"


def test_receiver_ignores_uninterpretable_packet():
    # Uninterpretable packet -> no callback -> wait_for runs into a timeout.
    with pytest.raises(TimeoutError):
        _run(_receive_one(b"junk"))
