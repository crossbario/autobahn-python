# SPDX-License-Identifier: MIT

import asyncio
import os

import pytest

from autobahn.asyncio.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    WebSocketServerFactory,
    WebSocketServerProtocol,
)

pytestmark = pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)

MESSAGE_COUNT = 3000
HANDLER_DELAY = 0.05
PENDING_LIMIT = 64


class SendingClient(WebSocketClientProtocol):
    def onOpen(self):
        self.factory.opened.set_result(None)


class CountingServer(WebSocketServerProtocol):
    def onOpen(self):
        self.pending = 0
        self.peak = 0
        self.received = 0
        self.factory.connection = self

    def begin_message(self):
        self.pending += 1
        self.peak = max(self.peak, self.pending)

    def finish_message(self):
        self.pending -= 1
        self.received += 1
        if self.received == MESSAGE_COUNT:
            self.factory.finished.set_result(None)


class AsyncMessageServer(CountingServer):
    async def onMessage(self, payload, isBinary):
        self.begin_message()
        try:
            await asyncio.sleep(HANDLER_DELAY)
        finally:
            self.finish_message()


class SyncMessageServer(CountingServer):
    def onMessage(self, payload, isBinary):
        self.begin_message()
        self.finish_message()


async def send_messages(server_protocol):
    loop = asyncio.get_running_loop()
    server_factory = WebSocketServerFactory()
    server_factory.protocol = server_protocol
    server_factory.finished = loop.create_future()
    server = await loop.create_server(server_factory, "127.0.0.1", 0)
    try:
        port = server.sockets[0].getsockname()[1]
        client_factory = WebSocketClientFactory(f"ws://127.0.0.1:{port}")
        client_factory.protocol = SendingClient
        client_factory.opened = loop.create_future()
        client_transport, client = await loop.create_connection(
            client_factory, "127.0.0.1", port
        )
        try:
            await asyncio.wait_for(client_factory.opened, 2)
            for _ in range(MESSAGE_COUNT):
                client.sendMessage(b"small message")
            await asyncio.wait_for(server_factory.finished, 3)
            connection = server_factory.connection
            assert connection.received == MESSAGE_COUNT
            assert connection.pending == 0
            return connection.peak
        finally:
            client_transport.close()
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
@pytest.mark.xfail(strict=True, reason="#2069: async onMessage work is unbounded")
async def test_async_on_message_pending_handlers_are_bounded():
    peak = await send_messages(AsyncMessageServer)
    assert peak <= PENDING_LIMIT, f"peak pending handlers: {peak}"


@pytest.mark.asyncio
async def test_sync_on_message_has_one_pending_handler():
    peak = await send_messages(SyncMessageServer)
    assert peak == 1
