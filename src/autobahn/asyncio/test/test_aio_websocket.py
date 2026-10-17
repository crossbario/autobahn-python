###############################################################################
#
#  Copyright (C) typedef int GmbH
#  SPDX-License-Identifier: MIT
#
###############################################################################
import asyncio
import os

# because py.test tries to collect it as a test-case
from unittest.mock import Mock

import pytest
import txaio

from autobahn.asyncio.websocket import WebSocketServerFactory


async def echo_async(what, when):
    await asyncio.sleep(when)
    return what


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
@pytest.mark.asyncio
async def test_echo_async():
    assert "Hello!" == await echo_async("Hello!", 0)


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_websocket_custom_loop():
    factory = WebSocketServerFactory(loop=asyncio.new_event_loop())
    server = factory()
    transport = Mock()
    server.connection_made(transport)


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_async_on_connect_server():
    num = 42
    done = txaio.create_future()
    values = []

    async def foo(x):
        await asyncio.sleep(1)
        return x * x

    async def on_connect(req):
        v = await foo(num)
        values.append(v)
        txaio.resolve(done, req)

    factory = WebSocketServerFactory()
    server = factory()
    server.onConnect = on_connect
    transport = Mock()

    server.connection_made(transport)
    server.data = b"\r\n".join(
        [
            b"GET /ws HTTP/1.1",
            b"Host: www.example.com",
            b"Sec-WebSocket-Version: 13",
            b"Origin: http://www.example.com.malicious.com",
            b"Sec-WebSocket-Extensions: permessage-deflate",
            b"Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==",
            b"Connection: keep-alive, Upgrade",
            b"Upgrade: websocket",
            b"\r\n",  # last string doesn't get a \r\n from join()
        ]
    )
    server.processHandshake()

    asyncio.get_event_loop().run_until_complete(done)

    assert len(values) == 1
    assert values[0] == num * num


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_corrupt_compressed_frame_closes_connection():
    # A compressed frame that does not decompress must fail the connection
    # (#1986). It must not stop the asyncio receive loop and leave the
    # connection open.
    from autobahn.websocket.compress import (
        PerMessageDeflateOffer,
        PerMessageDeflateOfferAccept,
    )

    def accept(offers):
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                return PerMessageDeflateOfferAccept(offer)

    loop = asyncio.new_event_loop()
    try:
        factory = WebSocketServerFactory(loop=loop)
        factory.setProtocolOptions(perMessageCompressionAccept=accept)
        server = factory()
        transport = Mock()
        server.connection_made(transport)

        server.data_received(
            b"\r\n".join(
                [
                    b"GET /ws HTTP/1.1",
                    b"Host: www.example.com",
                    b"Sec-WebSocket-Version: 13",
                    b"Sec-WebSocket-Extensions: permessage-deflate",
                    b"Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==",
                    b"Connection: keep-alive, Upgrade",
                    b"Upgrade: websocket",
                    b"\r\n",  # last string doesn't get a \r\n from join()
                ]
            )
        )
        loop.run_until_complete(asyncio.sleep(0.1))
        assert server.state == server.STATE_OPEN
        assert server._perMessageCompress is not None

        # masked, FIN, RSV1 (compressed), binary frame with a corrupt body
        body = b"\xff" * 64
        mask = b"\x11\x22\x33\x44"
        frame = bytes([0x80 | 0x40 | 0x02, 0x80 | len(body)]) + mask
        frame += bytes(b ^ mask[i % 4] for i, b in enumerate(body))
        server.data_received(frame)
        loop.run_until_complete(asyncio.sleep(0.1))

        assert transport.close.called or transport.abort.called, (
            "connection left open after a corrupt compressed frame"
        )
    finally:
        loop.close()


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_unhandled_error_in_received_data_drops_connection():
    # Any exception escaping the protocol's data processing must drop the
    # connection, as on Twisted (#1986) - not stop the asyncio receive loop
    # and leave the connection open.
    loop = asyncio.new_event_loop()
    try:
        factory = WebSocketServerFactory(loop=loop)
        server = factory()
        transport = Mock()
        server.connection_made(transport)

        def broken(data):
            raise RuntimeError("bug in data processing")

        server._dataReceived = broken
        server.data_received(b"anything")
        loop.run_until_complete(asyncio.sleep(0.1))

        assert transport.abort.called
    finally:
        loop.close()
