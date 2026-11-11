###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

"""
Regression tests for autobahn-python#2053 (asyncio).
"""

import os
from unittest.mock import Mock

import pytest

from autobahn.asyncio.rawsocket import WampRawSocketServerProtocol
from autobahn.asyncio.websocket import WebSocketServerProtocol
from autobahn.wamp.exception import TransportLost

pytestmark = pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)


def _rawsocket_server():
    proto = WampRawSocketServerProtocol()
    proto.factory = Mock()
    proto.log = Mock()
    proto.connection_made(Mock())
    return proto


def test_rawsocket_close_before_handshake_logs_no_warning():
    # A connection that closes before the RawSocket opening handshake (a port
    # scan, a health check) has no session. Closing it used to log a warning
    # that ApplicationSession.onClose raised AttributeError.
    proto = _rawsocket_server()
    proto.connection_lost(None)
    proto.log.warn.assert_not_called()


def test_rawsocket_close_after_handshake_closes_session():
    proto = _rawsocket_server()
    session = Mock()
    proto._session = session
    proto.connection_lost(None)
    session.onClose.assert_called_once_with(True)
    proto.log.warn.assert_not_called()
    assert proto._session is None


def test_rawsocket_send_string_after_connection_lost():
    # e.g. sending from onClose: TransportLost, not AttributeError on None
    proto = _rawsocket_server()
    proto.connection_lost(None)
    with pytest.raises(TransportLost):
        proto.sendString(b"hello")


def test_websocket_close_connection_after_connection_lost():
    # closing a connection that is already gone is a no-op
    proto = WebSocketServerProtocol()
    proto.transport = None
    proto._closeConnection()
    proto._closeConnection(abort=True)
