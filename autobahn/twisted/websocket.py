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

from base64 import b64encode, b64decode

from zope.interface import implementer

import txaio
txaio.use_twisted()

import twisted.internet.protocol
from twisted.internet import endpoints
from twisted.internet.interfaces import ITransport, ISSLTransport

from twisted.internet.error import ConnectionDone, ConnectionAborted, \
    ConnectionLost
from twisted.internet.defer import Deferred

from autobahn.util import public
from autobahn.util import _is_tls_error, _maybe_tls_reason
from autobahn.wamp import websocket
from autobahn.websocket.types import ConnectionRequest, ConnectionResponse, ConnectionDeny, \
    TransportDetails
from autobahn.websocket import protocol
from autobahn.websocket.interfaces import IWebSocketClientAgent
from autobahn.twisted.util import peer2str, transport_channel_id

from autobahn.websocket.compress import PerMessageDeflateOffer, \
    PerMessageDeflateOfferAccept, \
    PerMessageDeflateResponse, \
    PerMessageDeflateResponseAccept


__all__ = (
    'create_client_agent',

    'WebSocketAdapterProtocol',
    'WebSocketServerProtocol',
    'WebSocketClientProtocol',
    'WebSocketAdapterFactory',
    'WebSocketServerFactory',
    'WebSocketClientFactory',

    'WrappingWebSocketAdapter',
    'WrappingWebSocketServerProtocol',
    'WrappingWebSocketClientProtocol',
    'WrappingWebSocketServerFactory',
    'WrappingWebSocketClientFactory',

    'listenWS',
    'connectWS',

    'WampWebSocketServerProtocol',
    'WampWebSocketServerFactory',
    'WampWebSocketClientProtocol',
    'WampWebSocketClientFactory',
)


def create_client_agent(reactor):
    """
    :returns: an instance implementing IWebSocketClientAgent
    """
    return _TwistedWebSocketClientAgent(reactor)


def check_transport_config(transport_config):
    """
    raises a ValueError if `transport_config` is invalid
    """
    # XXX move me to "autobahn.websocket.util"
    if not isinstance(transport_config, str):
        raise ValueError(
            "'transport_config' must be a string, found {}".format(type(transport_config))
        )
    # XXX also accept everything Crossbar has in client transport configs? e.g like:
    # { "type": "websocket", "endpoint": {"type": "tcp", "host": "example.com", ...}}
    # XXX what about TLS options? (the above point would address that too)
    if not transport_config.startswith("ws://") and \
       not transport_config.startswith("wss://"):
        raise ValueError(
            "'transport_config' must start with 'ws://' or 'wss://'"
        )
    return None


def check_client_options(options):
    """
    raises a ValueError if `options` is invalid
    """
    # XXX move me to "autobahn.websocket.util"
    if not isinstance(options, dict):
        raise ValueError(
            "'options' must be a dict"
        )

    # anything that WebSocketClientFactory accepts (at least)
    valid_keys = [
        "origin",
        "protocols",
        "useragent",
        "headers",
        "proxy",
    ]
    for actual_k in options.keys():
        if actual_k not in valid_keys:
            raise ValueError(
                "'options' may not contain '{}'".format(actual_k)
            )


def _endpoint_from_config(reactor, factory, transport_config, options):
    # XXX might want some Crossbar code here? e.g. if we allow
    # "transport_config" to be a dict etc.

    # ... passing in the Factory is weird, but that's what parses all
    # the options and the URL currently

    if factory.isSecure:
        # create default client SSL context factory when none given
        from twisted.internet import ssl
        context_factory = ssl.optionsForClientTLS(factory.host)

    if factory.proxy is not None:
        factory.contextFactory = context_factory
        endpoint = endpoints.HostnameEndpoint(
            reactor,
            factory.proxy['host'],
            factory.proxy['port'],
            # timeout,  option?
        )
    else:
        if factory.isSecure:
            from twisted.internet import ssl
            endpoint = endpoints.SSL4ClientEndpoint(
                reactor,
                factory.host,
                factory.port,
                context_factory,
                # timeout,  option?
            )
        else:
            endpoint = endpoints.HostnameEndpoint(  # XXX right? not TCP4ClientEndpoint
                reactor,
                factory.host,
                factory.port,
                # timeout,  option?
                # attemptDelay,  option?
            )
    return endpoint


class _TwistedWebSocketClientAgent(IWebSocketClientAgent):
    """
    This agent creates connections using Twisted
    """

    def __init__(self, reactor):
        self._reactor = reactor

    def open(self, transport_config, options, protocol_class=None):
        """
        Open a new connection.

        :param dict transport_config: valid transport configuration

        :param dict options: additional options for the factory

        :param protocol_class: a callable that returns an instance of
            the protocol (WebSocketClientProtocol if the default None
            is passed in)

        :returns: a Deferred that fires with an instance of
            `protocol_class` (or WebSocketClientProtocol by default)
            that has successfully shaken hands (completed the
            handshake).
        """
        check_transport_config(transport_config)
        check_client_options(options)

        factory = WebSocketClientFactory(
            url=transport_config,
            reactor=self._reactor,
            **options
        )
        factory.protocol = WebSocketClientProtocol if protocol_class is None else protocol_class
        # XXX might want "contextFactory" for TLS ...? (or e.g. CA etc options?)

        endpoint = _endpoint_from_config(self._reactor, factory, transport_config, options)

        rtn_d = Deferred()
        proto_d = endpoint.connect(factory)

        def failed(f):
            rtn_d.errback(f)

        def got_proto(proto):

            def handshake_completed(arg):
                rtn_d.callback(proto)
                return arg
            proto.is_open.addCallbacks(handshake_completed, failed)
            return proto
        proto_d.addCallbacks(got_proto, failed)
        return rtn_d


class WebSocketAdapterProtocol(twisted.internet.protocol.Protocol):
    """
    Adapter class for Twisted WebSocket client and server protocols.
    """

    log = txaio.make_logger()

    peer = None
    peer_transport = None

    def connectionMade(self):
        # the peer we are connected to
        try:
            self.peer = peer2str(self.transport.getPeer())
        except AttributeError:
            # ProcessProtocols lack getPeer()
            self.peer = 'process:{}'.format(self.transport.pid)
        self.peer_transport = 'websocket'

        self._connectionMade()
        self.log.debug('Connection made to {peer}', peer=self.peer)

        # Set "Nagle"
        try:
            self.transport.setTcpNoDelay(self.tcpNoDelay)
        except:  # don't touch this! does not work: AttributeError, OSError
            # eg Unix Domain sockets throw Errno 22 on this
            pass

    def connectionLost(self, reason):
        if isinstance(reason.value, ConnectionDone):
            self.log.debug("Connection to/from {peer} was closed cleanly",
                           peer=self.peer)

        elif _is_tls_error(reason.value):
            self.log.error(_maybe_tls_reason(reason.value))

        elif isinstance(reason.value, ConnectionAborted):
            self.log.debug("Connection to/from {peer} was aborted locally",
                           peer=self.peer)

        elif isinstance(reason.value, ConnectionLost):
            message = str(reason.value)
            if hasattr(reason.value, 'message'):
                message = reason.value.message
            self.log.debug(
                "Connection to/from {peer} was lost in a non-clean fashion: {message}",
                peer=self.peer,
                message=message,
            )

        # at least: FileDescriptorOverrun, ConnectionFdescWentAway - but maybe others as well?
        else:
            self.log.debug("Connection to/from {peer} lost ({error_type}): {error})",
                           peer=self.peer, error_type=type(reason.value), error=reason.value)

        self._connectionLost(reason)

    def dataReceived(self, data):
        self._dataReceived(data)

    def _closeConnection(self, abort=False):
        if abort and hasattr(self.transport, 'abortConnection'):
            self.transport.abortConnection()
        else:
            # e.g. ProcessProtocol lacks abortConnection()
            self.transport.loseConnection()

    def _onOpen(self):
        self.onOpen()

    def _onMessageBegin(self, isBinary):
        self.onMessageBegin(isBinary)

    def _onMessageFrameBegin(self, length):
        self.onMessageFrameBegin(length)

    def _onMessageFrameData(self, payload):
        self.onMessageFrameData(payload)

    def _onMessageFrameEnd(self):
        self.onMessageFrameEnd()

    def _onMessageFrame(self, payload):
        self.onMessageFrame(payload)

    def _onMessageEnd(self):
        self.onMessageEnd()

    def _onMessage(self, payload, isBinary):
        self.onMessage(payload, isBinary)

    def _onPing(self, payload):
        self.onPing(payload)

    def _onPong(self, payload):
        self.onPong(payload)

    def _onClose(self, wasClean, code, reason):
        self.onClose(wasClean, code, reason)

    def registerProducer(self, producer, streaming):
        """
        Register a Twisted producer with this protocol.

        :param producer: A Twisted push or pull producer.
        :type producer: object
        :param streaming: Producer type.
        :type streaming: bool
        """
        self.transport.registerProducer(producer, streaming)

    def unregisterProducer(self):
        """
        Unregister Twisted producer with this protocol.
        """
        self.transport.unregisterProducer()


@public
class WebSocketServerProtocol(WebSocketAdapterProtocol, protocol.WebSocketServerProtocol):
    """
    Base class for Twisted-based WebSocket server protocols.

    Implements :class:`autobahn.websocket.interfaces.IWebSocketChannel`.
    """

    log = txaio.make_logger()

    def get_channel_id(self, channel_id_type=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`
        """
        return transport_channel_id(self.transport, True, channel_id_type)


@public
class WebSocketClientProtocol(WebSocketAdapterProtocol, protocol.WebSocketClientProtocol):
    """
    Base class for Twisted-based WebSocket client protocols.

    Implements :class:`autobahn.websocket.interfaces.IWebSocketChannel`.
    """

    log = txaio.make_logger()

    def _onConnect(self, response):
        self.onConnect(response)

    def startTLS(self):
        self.log.debug("Starting TLS upgrade")
        self.transport.startTLS(self.factory.contextFactory)

    def get_channel_id(self, channel_id_type=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`
        """
        return transport_channel_id(self.transport, False, channel_id_type)

    def _create_transport_details(self):
        """
        Internal helper.
        Base class calls this to create a TransportDetails
        """
        # note that ITLSTransport exists too, which is "a TCP
        # transport that *can be upgraded* to TLS" .. if it *is*
        # upgraded to TLS, then the transport will implement
        # ISSLTransport at that point according to Twisted
        # documentation
        # the peer we are connected to
        is_secure = ISSLTransport.providedBy(self.transport)
        if is_secure:
            secure_channel_id = {
                'tls-unique': transport_channel_id(self.transport, False, 'tls-unique'),
            }
        else:
            secure_channel_id = {}
        return TransportDetails(peer=self.peer, is_secure=is_secure, secure_channel_id=secure_channel_id)


class WebSocketAdapterFactory(object):
    """
    Adapter class for Twisted-based WebSocket client and server factories.
    """


@public
class WebSocketServerFactory(WebSocketAdapterFactory, protocol.WebSocketServerFactory, twisted.internet.protocol.ServerFactory):
    """
    Base class for Twisted-based WebSocket server factories.

    Implements :class:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory`
    """

    def __init__(self, *args, **kwargs):
        """

        .. note::
            In addition to all arguments to the constructor of
            :meth:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory`,
            you can supply a ``reactor`` keyword argument to specify the
            Twisted reactor to be used.
        """
        # lazy import to avoid reactor install upon module import
        reactor = kwargs.pop('reactor', None)
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor

        protocol.WebSocketServerFactory.__init__(self, *args, **kwargs)


@public
class WebSocketClientFactory(WebSocketAdapterFactory, protocol.WebSocketClientFactory, twisted.internet.protocol.ClientFactory):
    """
    Base class for Twisted-based WebSocket client factories.

    Implements :class:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory`
    """

    def __init__(self, *args, **kwargs):
        """

        .. note::
            In addition to all arguments to the constructor of
            :func:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory`,
            you can supply a ``reactor`` keyword argument to specify the
            Twisted reactor to be used.
        """
        # lazy import to avoid reactor install upon module import
        reactor = kwargs.pop('reactor', None)
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor

        protocol.WebSocketClientFactory.__init__(self, *args, **kwargs)
        # we must up-call *before* we set up the contextFactory
        # because we need self.host etc to be set properly.
        if self.isSecure and self.proxy is not None:
            # if we have a proxy, then our factory will be used to
            # create the connection after CONNECT and if it's doing
            # TLS it needs a contextFactory
            from twisted.internet import ssl
            self.contextFactory = ssl.optionsForClientTLS(self.host)
        # NOTE: there's thus no way to send in our own
        # context-factory, nor any TLS options.

        # Possibly we should allow 'proxy' to contain an actual
        # IStreamClientEndpoint instance instead of configuration for
        # how to make one


@implementer(ITransport)
class WrappingWebSocketAdapter(object):
    """
    An adapter for stream-based transport over WebSocket.

    This follows `websockify <https://github.com/kanaka/websockify>`_
    and should be compatible with that.

    It uses WebSocket subprotocol negotiation and supports the
    following WebSocket subprotocols:

      - ``binary`` (or a compatible subprotocol)
      - ``base64``

    Octets are either transmitted as the payload of WebSocket binary
    messages when using the ``binary`` subprotocol (or an alternative
    binary compatible subprotocol), or encoded with Base64 and then
    transmitted as the payload of WebSocket text messages when using
    the ``base64`` subprotocol.
    """

    def onConnect(self, requestOrResponse):
        # Negotiate either the 'binary' or the 'base64' WebSocket subprotocol
        if isinstance(requestOrResponse, ConnectionRequest):
            request = requestOrResponse
            for p in request.protocols:
                if p in self.factory._subprotocols:
                    self._binaryMode = (p != 'base64')
                    return p
            raise ConnectionDeny(ConnectionDeny.NOT_ACCEPTABLE, 'this server only speaks {0} WebSocket subprotocols'.format(self.factory._subprotocols))
        elif isinstance(requestOrResponse, ConnectionResponse):
            response = requestOrResponse
            if response.protocol not in self.factory._subprotocols:
                self._fail_connection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, 'this client only speaks {0} WebSocket subprotocols'.format(self.factory._subprotocols))
            self._binaryMode = (response.protocol != 'base64')
        else:
            # should not arrive here
            raise Exception("logic error")

    def onOpen(self):
        self._proto.connectionMade()

    def onMessage(self, payload, isBinary):
        if isBinary != self._binaryMode:
            self._fail_connection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_UNSUPPORTED_DATA, 'message payload type does not match the negotiated subprotocol')
        else:
            if not isBinary:
                try:
                    payload = b64decode(payload)
                except Exception as e:
                    self._fail_connection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INVALID_PAYLOAD, 'message payload base64 decoding error: {0}'.format(e))
            self._proto.dataReceived(payload)

    # noinspection PyUnusedLocal
    def onClose(self, wasClean, code, reason):
        self._proto.connectionLost(None)

    def write(self, data):
        # part of ITransport
        assert(type(data) == bytes)
        if self._binaryMode:
            self.sendMessage(data, isBinary=True)
        else:
            data = b64encode(data)
            self.sendMessage(data, isBinary=False)

    def writeSequence(self, data):
        # part of ITransport
        for d in data:
            self.write(d)

    def loseConnection(self):
        # part of ITransport
        self.sendClose()

    def getPeer(self):
        # part of ITransport
        return self.transport.getPeer()

    def getHost(self):
        # part of ITransport
        return self.transport.getHost()


class WrappingWebSocketServerProtocol(WrappingWebSocketAdapter, WebSocketServerProtocol):
    """
    Server protocol for stream-based transport over WebSocket.
    """


class WrappingWebSocketClientProtocol(WrappingWebSocketAdapter, WebSocketClientProtocol):
    """
    Client protocol for stream-based transport over WebSocket.
    """


class WrappingWebSocketServerFactory(WebSocketServerFactory):
    """
    Wrapping server factory for stream-based transport over WebSocket.
    """

    def __init__(self,
                 factory,
                 url,
                 reactor=None,
                 enableCompression=True,
                 autoFragmentSize=0,
                 subprotocol=None):
        """

        :param factory: Stream-based factory to be wrapped.
        :type factory: A subclass of ``twisted.internet.protocol.Factory``
        :param url: WebSocket URL of the server this server factory will work for.
        :type url: unicode
        """
        self._factory = factory
        self._subprotocols = ['binary', 'base64']
        if subprotocol:
            self._subprotocols.append(subprotocol)

        WebSocketServerFactory.__init__(self,
                                        url=url,
                                        reactor=reactor,
                                        protocols=self._subprotocols)

        # automatically fragment outgoing traffic into WebSocket frames
        # of this size
        self.setProtocolOptions(autoFragmentSize=autoFragmentSize)

        # play nice and perform WS closing handshake
        self.setProtocolOptions(failByDrop=False)

        if enableCompression:
            # Enable WebSocket extension "permessage-deflate".

            # Function to accept offers from the client ..
            def accept(offers):
                for offer in offers:
                    if isinstance(offer, PerMessageDeflateOffer):
                        return PerMessageDeflateOfferAccept(offer)

            self.setProtocolOptions(perMessageCompressionAccept=accept)

    def buildProtocol(self, addr):
        proto = WrappingWebSocketServerProtocol()
        proto.factory = self
        proto._proto = self._factory.buildProtocol(addr)
        proto._proto.transport = proto
        return proto

    def startFactory(self):
        self._factory.startFactory()
        WebSocketServerFactory.startFactory(self)

    def stopFactory(self):
        self._factory.stopFactory()
        WebSocketServerFactory.stopFactory(self)


class WrappingWebSocketClientFactory(WebSocketClientFactory):
    """
    Wrapping client factory for stream-based transport over WebSocket.
    """

    def __init__(self,
                 factory,
                 url,
                 reactor=None,
                 enableCompression=True,
                 autoFragmentSize=0,
                 subprotocol=None):
        """

        :param factory: Stream-based factory to be wrapped.
        :type factory: A subclass of ``twisted.internet.protocol.Factory``
        :param url: WebSocket URL of the server this client factory will connect to.
        :type url: unicode
        """
        self._factory = factory
        self._subprotocols = ['binary', 'base64']
        if subprotocol:
            self._subprotocols.append(subprotocol)

        WebSocketClientFactory.__init__(self,
                                        url=url,
                                        reactor=reactor,
                                        protocols=self._subprotocols)

        # automatically fragment outgoing traffic into WebSocket frames
        # of this size
        self.setProtocolOptions(autoFragmentSize=autoFragmentSize)

        # play nice and perform WS closing handshake
        self.setProtocolOptions(failByDrop=False)

        if enableCompression:
            # Enable WebSocket extension "permessage-deflate".

            # The extensions offered to the server ..
            offers = [PerMessageDeflateOffer()]
            self.setProtocolOptions(perMessageCompressionOffers=offers)

            # Function to accept responses from the server ..
            def accept(response):
                if isinstance(response, PerMessageDeflateResponse):
                    return PerMessageDeflateResponseAccept(response)

            self.setProtocolOptions(perMessageCompressionAccept=accept)

    def buildProtocol(self, addr):
        proto = WrappingWebSocketClientProtocol()
        proto.factory = self
        proto._proto = self._factory.buildProtocol(addr)
        proto._proto.transport = proto
        return proto


@public
def connectWS(factory, contextFactory=None, timeout=30, bindAddress=None):
    """
    Establish WebSocket connection to a server. The connection parameters like target
    host, port, resource and others are provided via the factory.

    :param factory: The WebSocket protocol factory to be used for creating client protocol instances.
    :type factory: An :class:`autobahn.websocket.WebSocketClientFactory` instance.

    :param contextFactory: SSL context factory, required for secure WebSocket connections ("wss").
    :type contextFactory: A `twisted.internet.ssl.ClientContextFactory <http://twistedmatrix.com/documents/current/api/twisted.internet.ssl.ClientContextFactory.html>`_ instance.

    :param timeout: Number of seconds to wait before assuming the connection has failed.
    :type timeout: int

    :param bindAddress: A (host, port) tuple of local address to bind to, or None.
    :type bindAddress: tuple

    :returns: The connector.
    :rtype: An object which implements `twisted.interface.IConnector <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IConnector.html>`_.
    """
    # lazy import to avoid reactor install upon module import
    if hasattr(factory, 'reactor'):
        reactor = factory.reactor
    else:
        from twisted.internet import reactor

    if factory.isSecure:
        if contextFactory is None:
            # create default client SSL context factory when none given
            from twisted.internet import ssl
            contextFactory = ssl.ClientContextFactory()

    if factory.proxy is not None:
        factory.contextFactory = contextFactory
        conn = reactor.connectTCP(factory.proxy['host'], factory.proxy['port'], factory, timeout, bindAddress)
    else:
        if factory.isSecure:
            conn = reactor.connectSSL(factory.host, factory.port, factory, contextFactory, timeout, bindAddress)
        else:
            conn = reactor.connectTCP(factory.host, factory.port, factory, timeout, bindAddress)
    return conn


@public
def listenWS(factory, contextFactory=None, backlog=50, interface=''):
    """
    Listen for incoming WebSocket connections from clients. The connection parameters like
    listening port and others are provided via the factory.

    :param factory: The WebSocket protocol factory to be used for creating server protocol instances.
    :type factory: An :class:`autobahn.websocket.WebSocketServerFactory` instance.

    :param contextFactory: SSL context factory, required for secure WebSocket connections ("wss").
    :type contextFactory: A twisted.internet.ssl.ContextFactory.

    :param backlog: Size of the listen queue.
    :type backlog: int

    :param interface: The interface (derived from hostname given) to bind to, defaults to '' (all).
    :type interface: str

    :returns: The listening port.
    :rtype: An object that implements `twisted.interface.IListeningPort <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IListeningPort.html>`_.
    """
    # lazy import to avoid reactor install upon module import
    if hasattr(factory, 'reactor'):
        reactor = factory.reactor
    else:
        from twisted.internet import reactor

    if factory.isSecure:
        if contextFactory is None:
            raise Exception("Secure WebSocket listen requested, but no SSL context factory given")
        listener = reactor.listenSSL(factory.port, factory, contextFactory, backlog, interface)
    else:
        listener = reactor.listenTCP(factory.port, factory, backlog, interface)
    return listener


@public
class WampWebSocketServerProtocol(websocket.WampWebSocketServerProtocol, WebSocketServerProtocol):
    """
    Twisted-based WAMP-over-WebSocket server protocol.

    Implements:

    * :class:`autobahn.wamp.interfaces.ITransport`
    """


@public
class WampWebSocketServerFactory(websocket.WampWebSocketServerFactory, WebSocketServerFactory):
    """
    Twisted-based WAMP-over-WebSocket server protocol factory.
    """

    protocol = WampWebSocketServerProtocol

    def __init__(self, factory, *args, **kwargs):
        """

        :param factory: A callable that produces instances that implement
            :class:`autobahn.wamp.interfaces.ITransportHandler`
        :type factory: callable

        :param serializers: A list of WAMP serializers to use (or ``None``
            for all available serializers).
        :type serializers: list of objects implementing
            :class:`autobahn.wamp.interfaces.ISerializer`
        """

        serializers = kwargs.pop('serializers', None)

        websocket.WampWebSocketServerFactory.__init__(self, factory, serializers)

        kwargs['protocols'] = self._protocols

        # noinspection PyCallByClass
        WebSocketServerFactory.__init__(self, *args, **kwargs)


@public
class WampWebSocketClientProtocol(websocket.WampWebSocketClientProtocol, WebSocketClientProtocol):
    """
    Twisted-based WAMP-over-WebSocket client protocol.

    Implements:

    * :class:`autobahn.wamp.interfaces.ITransport`
    """


@public
class WampWebSocketClientFactory(websocket.WampWebSocketClientFactory, WebSocketClientFactory):
    """
    Twisted-based WAMP-over-WebSocket client protocol factory.
    """

    protocol = WampWebSocketClientProtocol

    def __init__(self, factory, *args, **kwargs):
        """

        :param factory: A callable that produces instances that implement
            :class:`autobahn.wamp.interfaces.ITransportHandler`
        :type factory: callable

        :param serializer: The WAMP serializer to use (or ``None`` for
           "best" serializer, chosen as the first serializer available from
           this list: CBOR, MessagePack, UBJSON, JSON).
        :type serializer: object implementing :class:`autobahn.wamp.interfaces.ISerializer`
        """

        serializers = kwargs.pop('serializers', None)

        websocket.WampWebSocketClientFactory.__init__(self, factory, serializers)

        kwargs['protocols'] = self._protocols

        WebSocketClientFactory.__init__(self, *args, **kwargs)
