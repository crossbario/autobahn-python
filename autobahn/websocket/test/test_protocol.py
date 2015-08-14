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

from autobahn.websocket.protocol import WebSocketServerProtocol, WebSocketServerFactory


class FakeTransport(object):

    _written = b""

    def write(self, msg):
        self._written = self._written + msg


class WebSocketProtocolTests(unittest.TestCase):
    """
    Tests for autobahn.websocket.protocol.WebSocketProtocol.
    """
    def test_sendClose_none(self):
        """
        onClose with no code or reason works.
        """
        t = FakeTransport()
        f = WebSocketServerFactory()
        p = WebSocketServerProtocol()
        p.factory = f
        p.transport = t

        p._connectionMade()
        p.state = p.STATE_OPEN
        p.websocket_version = 18

        p.sendClose()

        # We closed properly
        self.assertEqual(t._written, b"\x88\x00")
        self.assertEqual(p.state, p.STATE_CLOSING)

    def test_sendClose_str_reason(self):
        """
        onClose with a str reason works.
        """
        t = FakeTransport()
        f = WebSocketServerFactory()
        p = WebSocketServerProtocol()
        p.factory = f
        p.transport = t

        p._connectionMade()
        p.state = p.STATE_OPEN
        p.websocket_version = 18

        p.sendClose(code=1000, reason="oh no")

        # We closed properly
        self.assertEqual(t._written, b"\x88\x00")
        self.assertEqual(p.state, p.STATE_CLOSING)
