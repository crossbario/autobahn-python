import pytest
import os

# because py.test tries to collect it as a test-case
try:
    from asyncio.test_utils import TestLoop as AsyncioTestLoop
except ImportError:
    from trollius.test_utils import TestLoop as AsyncioTestLoop
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from autobahn.asyncio.websocket import WebSocketServerFactory
from unittest import TestCase


@pytest.mark.usefixtures("event_loop")  # ensure we have pytest_asyncio installed
@pytest.mark.skipif(os.environ.get('USE_ASYNCIO', False), reason="Only for asyncio")
class Test(TestCase):

    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_websocket_custom_loop(self):

        def time_gen():
            yield
            yield

        loop = AsyncioTestLoop(time_gen)
        factory = WebSocketServerFactory(loop=loop)
        server = factory()
        transport = Mock()

        server.connection_made(transport)

    def test_async_on_connect_server(self):
        # see also issue 757

        async def foo(x):
            return x * x

        values = []
        async def on_connect(req):
            x = await foo(42)
            values.append(x)

        factory = WebSocketServerFactory()
        server = factory()
        server.onConnect = on_connect
        transport = Mock()

        server.connection_made(transport)
        # need/want to insert real-fake handshake data?
        server.data = b"\r\n".join([
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

        import asyncio
        from asyncio.test_utils import run_once
        run_once(asyncio.get_event_loop())

        self.assertEqual(1, len(values))
        self.assertEqual(42 * 42, values[0])
