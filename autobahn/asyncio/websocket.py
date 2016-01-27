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

from __future__ import absolute_import

from collections import deque

import txaio
txaio.use_asyncio()

from autobahn.wamp import websocket
from autobahn.websocket import protocol

try:
    import asyncio
    from asyncio import iscoroutine
    from asyncio import Future
except ImportError:
    # Trollius >= 0.3 was renamed
    # noinspection PyUnresolvedReferences
    import trollius as asyncio
    from trollius import iscoroutine
    from trollius import Future

from autobahn.websocket.types import ConnectionDeny


__all__ = (
    'WebSocketAdapterProtocol',
    'WebSocketServerProtocol',
    'WebSocketClientProtocol',
    'WebSocketAdapterFactory',
    'WebSocketServerFactory',
    'WebSocketClientFactory',
    'WampWebSocketServerProtocol',
    'WampWebSocketClientProtocol',
    'WampWebSocketServerFactory',
    'WampWebSocketClientFactory',
)


def yields(value):
    """
    Returns ``True`` iff the value yields.

    .. seealso:: http://stackoverflow.com/questions/20730248/maybedeferred-analog-with-asyncio
    """
    return isinstance(value, Future) or iscoroutine(value)


class WebSocketAdapterProtocol(asyncio.Protocol):
    """
    Adapter class for asyncio-based WebSocket client and server protocols.
    """

    def connection_made(self, transport):
        self.transport = transport

        self.receive_queue = deque()
        self._consume()

        try:
            peer = transport.get_extra_info('peername')
            try:
                # FIXME: tcp4 vs tcp6
                self.peer = u"tcp:%s:%d" % (peer[0], peer[1])
            except:
                # e.g. Unix Domain sockets don't have host/port
                self.peer = u"unix:{0}".format(peer)
        except:
            self.peer = u"?"

        self._connectionMade()

    def connection_lost(self, exc):
        self._connectionLost(exc)
        self.transport = None

    def _consume(self):
        self.waiter = Future()

        def process(_):
            while len(self.receive_queue):
                data = self.receive_queue.popleft()
                if self.transport:
                    self._dataReceived(data)
            self._consume()

        self.waiter.add_done_callback(process)

    def data_received(self, data):
        self.receive_queue.append(data)
        if not self.waiter.done():
            self.waiter.set_result(None)

    # noinspection PyUnusedLocal
    def _closeConnection(self, abort=False):
        self.transport.close()

    def _onOpen(self):
        res = self.onOpen()
        if yields(res):
            asyncio.async(res)

    def _onMessageBegin(self, isBinary):
        res = self.onMessageBegin(isBinary)
        if yields(res):
            asyncio.async(res)

    def _onMessageFrameBegin(self, length):
        res = self.onMessageFrameBegin(length)
        if yields(res):
            asyncio.async(res)

    def _onMessageFrameData(self, payload):
        res = self.onMessageFrameData(payload)
        if yields(res):
            asyncio.async(res)

    def _onMessageFrameEnd(self):
        res = self.onMessageFrameEnd()
        if yields(res):
            asyncio.async(res)

    def _onMessageFrame(self, payload):
        res = self.onMessageFrame(payload)
        if yields(res):
            asyncio.async(res)

    def _onMessageEnd(self):
        res = self.onMessageEnd()
        if yields(res):
            asyncio.async(res)

    def _onMessage(self, payload, isBinary):
        res = self.onMessage(payload, isBinary)
        if yields(res):
            asyncio.async(res)

    def _onPing(self, payload):
        res = self.onPing(payload)
        if yields(res):
            asyncio.async(res)

    def _onPong(self, payload):
        res = self.onPong(payload)
        if yields(res):
            asyncio.async(res)

    def _onClose(self, wasClean, code, reason):
        res = self.onClose(wasClean, code, reason)
        if yields(res):
            asyncio.async(res)

    def get_channel_id(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`
        """
        # FIXME
        raise Exception("transport channel binding not implemented for asyncio")

    def registerProducer(self, producer, streaming):
        raise Exception("not implemented")


class WebSocketServerProtocol(WebSocketAdapterProtocol, protocol.WebSocketServerProtocol):
    """
    Base class for asyncio-based WebSocket server protocols.
    """

    def _onConnect(self, request):
        # onConnect() will return the selected subprotocol or None
        # or a pair (protocol, headers) or raise an HttpException
        ##
        # noinspection PyBroadException
        try:
            res = self.onConnect(request)
            # if yields(res):
            #  res = yield from res
        except ConnectionDeny as e:
            self.failHandshake(e.reason, e.code)
        except Exception as e:
            self.failHandshake("Internal server error: {}".format(e), ConnectionDeny.INTERNAL_SERVER_ERROR)
        else:
            self.succeedHandshake(res)


class WebSocketClientProtocol(WebSocketAdapterProtocol, protocol.WebSocketClientProtocol):
    """
    Base class for asyncio-based WebSocket client protocols.
    """

    def _onConnect(self, response):
        res = self.onConnect(response)
        if yields(res):
            asyncio.async(res)

    def startTLS(self):
        raise Exception("WSS over explicit proxies not implemented")


class WebSocketAdapterFactory(object):
    """
    Adapter class for asyncio-based WebSocket client and server factories.
    """
    log = txaio.make_logger()

    def __call__(self):
        proto = self.protocol()
        proto.factory = self
        return proto


class WebSocketServerFactory(WebSocketAdapterFactory, protocol.WebSocketServerFactory):
    """
    Base class for asyncio-based WebSocket server factories.
    """

    def __init__(self, *args, **kwargs):
        """
        In addition to all arguments to the constructor of
        :class:`autobahn.websocket.protocol.WebSocketServerFactory`,
        you can supply a ``loop`` keyword argument to specify the
        asyncio event loop to be used.
        """
        loop = kwargs.pop('loop', None)
        self.loop = loop or asyncio.get_event_loop()

        protocol.WebSocketServerFactory.__init__(self, *args, **kwargs)


class WebSocketClientFactory(WebSocketAdapterFactory, protocol.WebSocketClientFactory):
    """
    Base class for asyncio-baseed WebSocket client factories.
    """

    def __init__(self, *args, **kwargs):
        """
        In addition to all arguments to the constructor of
        :class:`autobahn.websocket.protocol.WebSocketClientFactory`,
        you can supply a ``loop`` keyword argument to specify the
        asyncio event loop to be used.
        """
        loop = kwargs.pop('loop', None)
        self.loop = loop or asyncio.get_event_loop()

        protocol.WebSocketClientFactory.__init__(self, *args, **kwargs)


class WampWebSocketServerProtocol(websocket.WampWebSocketServerProtocol, WebSocketServerProtocol):
    """
    Base class for asyncio-based WAMP-over-WebSocket server protocols.
    """


class WampWebSocketServerFactory(websocket.WampWebSocketServerFactory, WebSocketServerFactory):
    """
    Base class for asyncio-based WAMP-over-WebSocket server factories.
    """

    protocol = WampWebSocketServerProtocol

    def __init__(self, factory, *args, **kwargs):

        serializers = kwargs.pop('serializers', None)

        websocket.WampWebSocketServerFactory.__init__(self, factory, serializers)

        kwargs['protocols'] = self._protocols

        # noinspection PyCallByClass
        WebSocketServerFactory.__init__(self, *args, **kwargs)


class WampWebSocketClientProtocol(websocket.WampWebSocketClientProtocol, WebSocketClientProtocol):
    """
    Base class for asyncio-based WAMP-over-WebSocket client protocols.
    """


class WampWebSocketClientFactory(websocket.WampWebSocketClientFactory, WebSocketClientFactory):
    """
    Base class for asyncio-based WAMP-over-WebSocket client factories.
    """

    protocol = WampWebSocketClientProtocol

    def __init__(self, factory, *args, **kwargs):

        serializers = kwargs.pop('serializers', None)

        websocket.WampWebSocketClientFactory.__init__(self, factory, serializers)

        kwargs['protocols'] = self._protocols

        WebSocketClientFactory.__init__(self, *args, **kwargs)
