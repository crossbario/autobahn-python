###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

from __future__ import absolute_import

from twisted.internet.defer import inlineCallbacks
from twisted.internet.address import IPv4Address
from twisted.internet._resolver import HostResolution  # FIXME
from twisted.internet.interfaces import ISSLTransport, IReactorPluggableNameResolver, IHostnameResolver
from twisted.test.proto_helpers import MemoryReactorClock
from twisted.test import iosim

from zope.interface import directlyProvides, implementer

from autobahn.websocket.interfaces import IWebSocketClientAgent
from autobahn.twisted.websocket import _TwistedWebSocketClientAgent
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketClientProtocol


__all__ = (
    'create_memory_agent',
)


@implementer(IHostnameResolver)
class TestResolver(object):
    def resolveHostName(self, receiver, hostName, portNumber=0):
        """
        'really' from IReactorPluggableNameResolver for MemoryReactor
        FIXME
        """
        resolution = HostResolution(hostName)
        receiver.resolutionBegan(resolution)
        receiver.addressResolved(
            IPv4Address('TCP', '127.0.0.1', 31337 if portNumber == 0 else portNumber)
        )
        receiver.resolutionComplete()


@implementer(IReactorPluggableNameResolver)
class _Resolver(object):

    _resolver = None

    @property
    def nameResolver(self):
        if self._resolver is None:
            self._resolver = TestResolver()
        return self._resolver

    def installNameResolver(self, resolver):
        old = self._resolver
        self._resolver = resolver
        return old


class MemoryReactorClockResolver(MemoryReactorClock, _Resolver):
    """
    Are we **inheriting enough** yet??
    """
    pass


class _TwistedWebMemoryAgent(IWebSocketClientAgent):
    """
    A testing agent.
    """

    def __init__(self, reactor, client_protocol, server_protocol):
        self._reactor = reactor
        self._server_protocol = server_protocol
        self._client_protocol = client_protocol

        # our "real" underlying agent under test
        self._agent = _TwistedWebSocketClientAgent(self._reactor)
        self._pumps = set()
        self._servers = dict()  # client -> server

    def open(self, transport_config, options, protocol_class=None):
        """
        This is some proof-of-concept level hacking to see that we can set
        up an IOPump properly and get a client -> server message
        through (see autobahn/twisted/test/test_websocket_agent.py
        """
        # call our "real" agent
        real_client_protocol = self._agent.open(
            transport_config, options,
            protocol_class=protocol_class,
        )

        # wss vs ws
        # host, port, factory, context_factory, timeout, bindAddress = (
        #     self._memoryReactor.sslClients[-1])
        host, port, factory, timeout, bindAddress = self._reactor.tcpClients[-1]

        serverAddress = IPv4Address('TCP', '127.0.0.1', port)
        clientAddress = IPv4Address('TCP', '127.0.0.1', 31337)

        serverProtocol = self._server_protocol()
        serverProtocol.factory = WebSocketServerFactory()

        serverTransport = iosim.FakeTransport(
            serverProtocol, isServer=True,
            hostAddress=serverAddress, peerAddress=clientAddress)
        clientProtocol = factory.buildProtocol(None)
        clientTransport = iosim.FakeTransport(
            clientProtocol, isServer=False,
            hostAddress=clientAddress, peerAddress=serverAddress)

        if "wss":
            directlyProvides(serverTransport, ISSLTransport)
            directlyProvides(clientTransport, ISSLTransport)

        pump = iosim.connect(
            serverProtocol, serverTransport, clientProtocol, clientTransport)
        self._pumps.add(pump)

        def add_mapping(proto):
            self._servers[proto] = serverProtocol
            return proto
        real_client_protocol.addCallback(add_mapping)
        return real_client_protocol

    def flush(self):
        """
        (XXX copied from treq, MIT license)
        (XXX not sure if we need this? change docs if so)
        Flush all data between pending client/server pairs.

        This is only necessary if a :obj:`Resource` under test returns
        :obj:`NOT_DONE_YET` from its ``render`` method, making a response
        asynchronous. In that case, after each write from the server,
        :meth:`pump` must be called so the client can see it.
        """
        old_pumps = self._pumps
        new_pumps = self._pumps = set()
        for p in old_pumps:
            p.flush()
            if p.clientIO.disconnected and p.serverIO.disconnected:
                continue
            new_pumps.add(p)

    def send_server_message_to_client(self, client, msg):
        """
        Is this an API that agent should have? (I'm playing with ways to
        build tests .. and tests will want to control what the server
        sends, and probably wait for client messages...
        """
        server_proto = self._servers[client]
        server_proto.sendMessage(msg)
        self.flush()


def create_memory_agent(reactor, client_protocol, server_protocol):
    """
    return a new instance implementing `IWebSocketClientAgent`.

    connection attempts will be satisfied by traversing the Upgrade
    request path starting at `resource` to find a `WebSocketResource`
    and then exchange data between client and server using purely
    in-memory buffers.
    """
    if client_protocol is None:
        client_protocol = WebSocketClientProtocol
    if server_protocol is None:
        server_protocol = WebSocketServerProtocol
    return _TwistedWebMemoryAgent(reactor, client_protocol, server_protocol)
