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

import unittest
from unittest.mock import Mock

from autobahn.twisted.rawsocket import (WampRawSocketServerFactory,
                                        WampRawSocketServerProtocol,
                                        WampRawSocketClientFactory,
                                        WampRawSocketClientProtocol)
from autobahn.testutil import FakeTransport


class RawSocketHandshakeTests(unittest.TestCase):

    def test_handshake_succeeds(self):
        """
        A client can connect to a server.
        """
        session_mock = Mock()
        t = FakeTransport()
        f = WampRawSocketClientFactory(lambda: session_mock)
        p = WampRawSocketClientProtocol()
        p.transport = t
        p.factory = f

        server_session_mock = Mock()
        st = FakeTransport()
        sf = WampRawSocketServerFactory(lambda: server_session_mock)
        sp = WampRawSocketServerProtocol()
        sp.transport = st
        sp.factory = sf

        sp.connectionMade()
        p.connectionMade()

        # Send the server the client handshake
        sp.dataReceived(t._written[0:1])
        sp.dataReceived(t._written[1:4])

        # Send the client the server handshake
        p.dataReceived(st._written)

        # The handshake succeeds, a session on each end is created
        # onOpen is called on the session
        session_mock.onOpen.assert_called_once_with(p)
        server_session_mock.onOpen.assert_called_once_with(sp)
