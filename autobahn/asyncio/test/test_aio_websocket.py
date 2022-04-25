import os
import asyncio
import pytest

import txaio

# because py.test tries to collect it as a test-case
from unittest.mock import Mock

from autobahn.asyncio.websocket import WebSocketServerFactory

# https://medium.com/ideas-at-igenius/testing-asyncio-python-code-with-pytest-a2f3628f82bc


async def echo_async(what, when):
    await asyncio.sleep(when)
    return what


@pytest.mark.skipif(not os.environ.get('USE_ASYNCIO', False), reason='test runs on asyncio only')
@pytest.mark.asyncio
async def test_echo_async():
    assert 'Hello!' == await echo_async('Hello!', 0)


# @pytest.mark.asyncio(forbid_global_loop=True)
@pytest.mark.skipif(not os.environ.get('USE_ASYNCIO', False), reason='test runs on asyncio only')
def test_websocket_custom_loop(event_loop):
    factory = WebSocketServerFactory(loop=event_loop)
    server = factory()
    transport = Mock()
    server.connection_made(transport)


@pytest.mark.skipif(not os.environ.get('USE_ASYNCIO', False), reason='test runs on asyncio only')
@pytest.mark.asyncio
async def test_async_on_connect_server(event_loop):

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
    server.data = b'\r\n'.join([
        b'GET /ws HTTP/1.1',
        b'Host: www.example.com',
        b'Sec-WebSocket-Version: 13',
        b'Origin: http://www.example.com.malicious.com',
        b'Sec-WebSocket-Extensions: permessage-deflate',
        b'Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==',
        b'Connection: keep-alive, Upgrade',
        b'Upgrade: websocket',
        b'\r\n',  # last string doesn't get a \r\n from join()
    ])
    server.processHandshake()
    await done

    assert len(values) == 1
    assert values[0] == num * num
