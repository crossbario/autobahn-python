###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
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

from __future__ import absolute_import, print_function

import unittest2 as unittest
from mock import Mock

from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.python.failure import Failure
from twisted.internet.error import ConnectionDone, ConnectionAborted, \
    ConnectionLost
from autobahn.test import FakeTransport


class ExceptionHandlingTests(unittest.TestCase):
    """
    Tests that we format various exception variations properly during
    connectionLost
    """

    def setUp(self):
        self.factory = WebSocketServerFactory()
        self.proto = WebSocketServerProtocol()
        self.proto.factory = self.factory
        self.proto.log = Mock()

    def tearDown(self):
        for call in [
                self.proto.autoPingPendingCall,
                self.proto.autoPingTimeoutCall,
                self.proto.openHandshakeTimeoutCall,
                self.proto.closeHandshakeTimeoutCall,
        ]:
            if call is not None:
                call.cancel()

    def test_connection_done(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionDone()))

        messages = ' '.join([str(x[1]) for x in self.proto.log.mock_calls])
        self.assertTrue('closed cleanly' in messages)

    def test_connection_aborted(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionAborted()))

        messages = ' '.join([str(x[1]) for x in self.proto.log.mock_calls])
        self.assertTrue(' aborted ' in messages)

    def test_connection_lost(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionLost()))

        messages = ' '.join([str(x[1]) for x in self.proto.log.mock_calls])
        self.assertTrue(' was lost ' in messages)

    def test_connection_lost_arg(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionLost("greetings")))

        messages = ' '.join([str(x[1]) + str(x[2]) for x in self.proto.log.mock_calls])
        self.assertTrue(' was lost ' in messages)
        self.assertTrue('greetings' in messages)


class Hixie76RejectionTests(unittest.TestCase):
    """
    Hixie-76 should not be accepted by an Autobahn server.
    """
    def test_handshake_fails(self):
        """
        A handshake from a client only supporting Hixie-76 will fail.
        """
        t = FakeTransport()
        f = WebSocketServerFactory()
        p = WebSocketServerProtocol()
        p.factory = f
        p.transport = t

        # from http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76
        http_request = b"GET /demo HTTP/1.1\r\nHost: example.com\r\nConnection: Upgrade\r\nSec-WebSocket-Key2: 12998 5 Y3 1  .P00\r\nSec-WebSocket-Protocol: sample\r\nUpgrade: WebSocket\r\nSec-WebSocket-Key1: 4 @1  46546xW%0l 1 5\r\nOrigin: http://example.com\r\n\r\n^n:ds[4U"

        p.openHandshakeTimeout = 0
        p._connectionMade()
        p.data = http_request
        p.processHandshake()
        self.assertIn(b"HTTP/1.1 400", t._written)
        self.assertIn(b"Hixie76 protocol not supported", t._written)
