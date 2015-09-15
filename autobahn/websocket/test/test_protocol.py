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

import os

import unittest2 as unittest

from autobahn.websocket.protocol import WebSocketServerProtocol
from autobahn.websocket.protocol import WebSocketServerFactory


class FakeTransport(object):
    _written = b""
    _open = True

    def write(self, msg):
        if not self._open:
            raise Exception("Can't write to a closed connection")
        self._written = self._written + msg

    def loseConnection(self):
        self._open = False


class Hixie76RejectionTests(unittest.TestCase):
    """
    Hixie-76 should not be accepted by an Autobahn server.
    """
    def test_handshake_fails(self):
        """
        A handshake from a client only supporting Hixie-76 will fail.
        """
        from autobahn.twisted.websocket import WebSocketServerFactory
        from autobahn.twisted.websocket import WebSocketServerProtocol

        t = FakeTransport()
        f = WebSocketServerFactory()
        p = WebSocketServerProtocol()
        p.factory = f
        p.transport = t

        # from http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76
        http_request = b"GET /demo HTTP/1.1\r\nHost: example.com\r\nConnection: Upgrade\r\nSec-WebSocket-Key2: 12998 5 Y3 1  .P00\r\nSec-WebSocket-Protocol: sample\r\nUpgrade: WebSocket\r\nSec-WebSocket-Key1: 4 @1  46546xW%0l 1 5\r\nOrigin: http://example.com\r\n\r\n^n:ds[4U"

        p._connectionMade()
        p.data = http_request
        p.processHandshake()
        self.assertIn("HTTP/1.1 400", t._written)
        self.assertIn("Hixie76 protocol not supported", t._written)


class WebSocketProtocolTests(unittest.TestCase):
    """
    Tests for autobahn.websocket.protocol.WebSocketProtocol.
    """
    def setUp(self):
        t = FakeTransport()
        f = WebSocketServerFactory()
        p = WebSocketServerProtocol()
        p.factory = f
        p.transport = t

        p._connectionMade()
        p.state = p.STATE_OPEN
        p.websocket_version = 18

        self.protocol = p
        self.transport = t

    def test_sendClose_none(self):
        """
        sendClose with no code or reason works.
        """
        self.protocol.sendClose()

        # We closed properly
        self.assertEqual(self.transport._written, b"\x88\x00")
        self.assertEqual(self.protocol.state, self.protocol.STATE_CLOSING)

    def test_sendClose_str_reason(self):
        """
        sendClose with a str reason works.
        """
        self.protocol.sendClose(code=1000, reason="oh no")

        # We closed properly
        self.assertEqual(self.transport._written[2:], b"\x03\xe8oh no")
        self.assertEqual(self.protocol.state, self.protocol.STATE_CLOSING)

    def test_sendClose_unicode_reason(self):
        """
        sendClose with a unicode reason works.
        """
        self.protocol.sendClose(code=1000, reason=u"oh no")

        # We closed properly
        self.assertEqual(self.transport._written[2:], b"\x03\xe8oh no")
        self.assertEqual(self.protocol.state, self.protocol.STATE_CLOSING)

    def test_sendClose_nonstr_reason(self):
        """
        sendClose with a non-str reason still closes the connection, coercing
        it to a string.
        """
        self.protocol.sendClose(code=1000, reason=12)

        # We closed properly
        self.assertEqual(self.transport._written[2:], b"\x03\xe812")
        self.assertEqual(self.protocol.state, self.protocol.STATE_CLOSING)

    def test_sendClose_toolong(self):
        """
        sendClose with a too-long reason will truncate it.
        """
        self.protocol.sendClose(code=1000, reason="abc" * 1000)

        # We closed properly
        self.assertEqual(self.transport._written[2:],
                         b"\x03\xe8" + (b"abc" * 40) + b"...")
        self.assertEqual(self.protocol.state, self.protocol.STATE_CLOSING)

    def test_sendClose_reason_with_no_code(self):
        """
        Trying to sendClose with a reason but no code will raise an Exception.
        """
        with self.assertRaises(Exception) as e:
            self.protocol.sendClose(reason="abc")

        self.assertIn("close reason without close code", str(e.exception))

        # We shouldn't have closed
        self.assertEqual(self.transport._written, b"")
        self.assertEqual(self.protocol.state, self.protocol.STATE_OPEN)

    def test_sendClose_invalid_code_type(self):
        """
        Trying to sendClose with a non-int code will raise an Exception.
        """
        with self.assertRaises(Exception) as e:
            self.protocol.sendClose(code="134")

        self.assertIn("invalid type ", str(e.exception))

        # We shouldn't have closed
        self.assertEqual(self.transport._written, b"")
        self.assertEqual(self.protocol.state, self.protocol.STATE_OPEN)

    def test_sendClose_invalid_code_value(self):
        """
        Trying to sendClose with a non-valid int code will raise an Exception.
        """
        with self.assertRaises(Exception) as e:
            self.protocol.sendClose(code=10)

        self.assertIn("invalid close code 10", str(e.exception))

        # We shouldn't have closed
        self.assertEqual(self.transport._written, b"")
        self.assertEqual(self.protocol.state, self.protocol.STATE_OPEN)


if not os.environ.get('USE_TWISTED', False):
    del Hixie76RejectionTests
