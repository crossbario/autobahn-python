import pytest
import os
import sys

# because py.test tries to collect it as a test-case
from unittest.mock import Mock

from autobahn.asyncio.websocket import WebSocketServerFactory
from unittest import TestCase
import txaio


@pytest.mark.skipif(True, reason='pytest sucks')
@pytest.mark.skipif(sys.version_info < (3, 3), reason="requires Python 3.3+")
@pytest.mark.skipif(os.environ.get('USE_ASYNCIO', False) is False, reason="only for asyncio")
@pytest.mark.usefixtures("event_loop")  # ensure we have pytest_asyncio installed
class Test(TestCase):

    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_websocket_custom_loop(self, event_loop):
        factory = WebSocketServerFactory(loop=event_loop)
        server = factory()
        transport = Mock()

        server.connection_made(transport)

    # not sure when this last worked, tests haven't been running
    # properly under asyncio for a while it seems.
    @pytest.mark.xfail
    def test_async_on_connect_server(self):
        # see also issue 757

        # for python 3.5, this can be "async def foo"
        def foo(x):
            f = txaio.create_future()
            txaio.resolve(f, x * x)
            return f

        values = []

        def on_connect(req):
            f = txaio.create_future()

            def cb(x):
                f = foo(42)
                f.add_callbacks(f, lambda v: values.append(v), None)
                return f
            txaio.add_callbacks(f, cb, None)
            return f

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

        self.assertEqual(1, len(values))
        self.assertEqual(42 * 42, values[0])
