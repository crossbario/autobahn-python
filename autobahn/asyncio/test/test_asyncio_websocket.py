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
