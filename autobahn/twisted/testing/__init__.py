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

from twisted.internet.defer import Deferred
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


__all__ = (
    'create_pumper',
    'create_memory_agent',
    'MemoryReactorClockResolver',
)


@implementer(IHostnameResolver)
class _LeetResolver(object):
    def resolveHostName(self, receiver, hostName, portNumber=0):
        """
        Implement IHostnameResolver which always returns 127.0.0.1:31337
        """
        resolution = HostResolution(hostName)
        receiver.resolutionBegan(resolution)
        receiver.addressResolved(
            IPv4Address('TCP', '127.0.0.1', 31337 if portNumber == 0 else portNumber)
        )
        receiver.resolutionComplete()


@implementer(IReactorPluggableNameResolver)
class _Resolver(object):
    """
    A test version of IReactorPluggableNameResolver
    """

    _resolver = None

    @property
    def nameResolver(self):
        if self._resolver is None:
            self._resolver = _LeetResolver()
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

    def __init__(self, reactor, pumper, server_protocol):
        self._reactor = reactor
        self._server_protocol = server_protocol
        self._pumper = pumper

        # our "real" underlying agent under test
        self._agent = _TwistedWebSocketClientAgent(self._reactor)
        self._pumps = set()
        self._servers = dict()  # client -> server

    def open(self, transport_config, options, protocol_class=None):
        """
        Implement IWebSocketClientAgent with in-memory transports.

        To 'see' data on the other side, `.flush()` must be called
        after data has been sent (e.g. after a sendMessage() call for
        example).
        """
        is_secure = transport_config.startswith("wss://")

        # call our "real" agent
        real_client_protocol = self._agent.open(
            transport_config, options,
            protocol_class=protocol_class,
        )

        if is_secure:
            host, port, factory, context_factory, timeout, bindAddress = self._reactor.sslClients[-1]
        else:
            host, port, factory, timeout, bindAddress = self._reactor.tcpClients[-1]

        server_address = IPv4Address('TCP', '127.0.0.1', port)
        client_address = IPv4Address('TCP', '127.0.0.1', 31337)

        server_protocol = self._server_protocol()
        server_protocol.factory = WebSocketServerFactory()

        server_transport = iosim.FakeTransport(
            server_protocol, isServer=True,
            hostAddress=server_address, peerAddress=client_address)
        clientProtocol = factory.buildProtocol(None)
        client_transport = iosim.FakeTransport(
            clientProtocol, isServer=False,
            hostAddress=client_address, peerAddress=server_address)

        if is_secure:
            directlyProvides(server_transport, ISSLTransport)
            directlyProvides(client_transport, ISSLTransport)

        pump = iosim.connect(
            server_protocol, server_transport, clientProtocol, client_transport)
        self._pumper.add(pump)

        def add_mapping(proto):
            self._servers[proto] = server_protocol
            return proto
        real_client_protocol.addCallback(add_mapping)
        return real_client_protocol


class _Kalamazoo(object):
    """
    Feeling whimsical about class names, see https://en.wikipedia.org/wiki/Handcar

    This is 'an IOPump pumper', an object which causes a series of
    IOPumps it is monitoring to do their I/O operations
    periodically. This needs the 'real' reactor which trial drives,
    because reasons:

     - so @inlineCallbacks / async-def functions work
       (if I could explain exactly why here, I would)

     - we need to 'break the loop' of synchronous calls somewhere and
       polluting the tests themselves with that is bad

     - get rid of e.g. .flush() calls in tests themselves (thus
      'teaching' the tests about details of I/O scheduling that they
      shouldn't know).
    """

    def __init__(self):
        self._pumps = set()
        self._pumping = False
        self._waiting_for_stop = []
        from twisted.internet import reactor as global_reactor
        self._global_reactor = global_reactor

    def add(self, p):
        """
        Add a new IOPump. It will be removed when both its client and
        server are disconnected.
        """
        self._pumps.add(p)

    def start(self):
        if self._pumping:
            return
        self._pumping = True
        self._global_reactor.callLater(0, self._pump_once)

    def stop(self):
        """
        :returns: a Deferred that fires when we have stopped pump()-ing

        Call from tearDown, for example.
        """
        if self._pumping or len(self._waiting_for_stop):
            d = Deferred()
            self._waiting_for_stop.append(d)
            self._pumping = False
            return d
        d = Deferred()
        d.callback(None)
        return d

    def _pump_once(self):
        """
        flush all data from all our IOPump instances and schedule another
        iteration on the global reactor
        """
        if self._pumping:
            self._flush()
            self._global_reactor.callLater(0.1, self._pump_once)
        else:
            for d in self._waiting_for_stop:
                d.callback(None)
            self._waiting_for_stop = []

    def _flush(self):
        """
        Flush all data between pending client/server pairs.
        """
        old_pumps = self._pumps
        new_pumps = self._pumps = set()
        for p in old_pumps:
            p.flush()
            if p.clientIO.disconnected and p.serverIO.disconnected:
                continue
            new_pumps.add(p)


def create_pumper():
    """
    return a new instance implementing IPumper
    """
    return _Kalamazoo()


def create_memory_agent(reactor, pumper, server_protocol):
    """
    return a new instance implementing `IWebSocketClientAgent`.

    connection attempts will be satisfied by traversing the Upgrade
    request path starting at `resource` to find a `WebSocketResource`
    and then exchange data between client and server using purely
    in-memory buffers.
    """
    if server_protocol is None:
        server_protocol = WebSocketServerProtocol
    return _TwistedWebMemoryAgent(reactor, pumper, server_protocol)
