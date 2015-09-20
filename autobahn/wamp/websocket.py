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

import traceback

from autobahn.websocket import protocol
from autobahn.websocket.types import ConnectionDeny
from autobahn.wamp.interfaces import ITransport
from autobahn.wamp.exception import ProtocolError, SerializationError, TransportLost

import txaio


__all__ = ('WampWebSocketServerProtocol',
           'WampWebSocketClientProtocol',
           'WampWebSocketServerFactory',
           'WampWebSocketClientFactory')


class WampWebSocketProtocol(object):
    """
    Base class for WAMP-over-WebSocket transport mixins.
    """

    _session = None  # default; self.session is set in onOpen

    def _bailout(self, code, reason=None):
        if self.factory.debug_wamp:
            print("Failing WAMP-over-WebSocket transport: code = {0}, reason = '{1}'".format(code, reason))
        self.failConnection(code, reason)

    def onOpen(self):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`
        """
        # WebSocket connection established. Now let the user WAMP session factory
        # create a new WAMP session and fire off session open callback.
        try:
            self._session = self.factory._factory()
            # self._session should be an ITransportHandler
            self._session.onOpen(self)
        except Exception as e:
            self.log.critical(traceback.format_exc())
            # Exceptions raised in onOpen are fatal ..
            reason = "WAMP Internal Error ({0})".format(e)
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason=reason)

    def onClose(self, wasClean, code, reason):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`
        """
        # WAMP session might never have been established in the first place .. guard this!
        if self._session is not None:
            # WebSocket connection lost - fire off the WAMP
            # session close callback
            # noinspection PyBroadException
            try:
                if self.factory.debug_wamp:
                    print("WAMP-over-WebSocket transport lost: wasClean = {0}, code = {1}, reason = '{2}'".format(wasClean, code, reason))
                self._session.onClose(wasClean)
            except Exception:
                self.log.critical(
                    "While calling onClose(): {traceback}",
                    traceback=txaio.failure_format_traceback(txaio.create_failure()),
                )
            self._session = None

    def onMessage(self, payload, isBinary):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`
        """
        try:
            for msg in self._serializer.unserialize(payload, isBinary):
                if self.factory.debug_wamp:
                    print("RX {0}".format(msg))
                self._session.onMessage(msg)

        except ProtocolError as e:
            self.log.critical(
                "While calling onMessage: {traceback}",
                traceback=txaio.failure_format_traceback(txaio.create_failure()),
            )
            reason = "WAMP Protocol Error ({0})".format(e)
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, reason=reason)

        except Exception as e:
            self.log.critical(traceback.format_exc())
            reason = "WAMP Internal Error ({0})".format(e)
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason=reason)

    def send(self, msg):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.send`
        """
        if self.isOpen():
            try:
                if self.factory.debug_wamp:
                    print("TX {0}".format(msg))
                payload, isBinary = self._serializer.serialize(msg)
            except Exception as e:
                # all exceptions raised from above should be serialization errors ..
                raise SerializationError("WAMP serialization error ({0})".format(e))
            else:
                self.sendMessage(payload, isBinary)
        else:
            raise TransportLost()

    def isOpen(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.isOpen`
        """
        return self._session is not None

    def close(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.close`
        """
        if self.isOpen():
            self.sendClose(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL)
        else:
            raise TransportLost()

    def abort(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.abort`
        """
        if self.isOpen():
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_GOING_AWAY)
        else:
            raise TransportLost()


ITransport.register(WampWebSocketProtocol)


def parseSubprotocolIdentifier(subprotocol):
    try:
        s = subprotocol.split('.')
        if s[0] != "wamp":
            raise Exception("invalid protocol %s" % s[0])
        version = int(s[1])
        serializerId = '.'.join(s[2:])
        return version, serializerId
    except:
        return None, None


class WampWebSocketServerProtocol(WampWebSocketProtocol):
    """
    Mixin for WAMP-over-WebSocket server transports.
    """

    STRICT_PROTOCOL_NEGOTIATION = True

    def onConnect(self, request):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
        """
        headers = {}
        for subprotocol in request.protocols:
            version, serializerId = parseSubprotocolIdentifier(subprotocol)
            if version == 2 and serializerId in self.factory._serializers.keys():
                self._serializer = self.factory._serializers[serializerId]
                return subprotocol, headers

        if self.STRICT_PROTOCOL_NEGOTIATION:
            raise ConnectionDeny(ConnectionDeny.BAD_REQUEST, "This server only speaks WebSocket subprotocols %s" % ', '.join(self.factory.protocols))
        else:
            # assume wamp.2.json
            self._serializer = self.factory._serializers['json']
            return None, headers


class WampWebSocketClientProtocol(WampWebSocketProtocol):
    """
    Mixin for WAMP-over-WebSocket client transports.
    """

    STRICT_PROTOCOL_NEGOTIATION = True

    def onConnect(self, response):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
        """
        if response.protocol not in self.factory.protocols:
            if self.STRICT_PROTOCOL_NEGOTIATION:
                raise Exception("Server does not speak any of the WebSocket subprotocols we requested (%s)." % ', '.join(self.factory.protocols))
            else:
                # assume wamp.2.json
                serializerId = 'json'
        else:
            version, serializerId = parseSubprotocolIdentifier(response.protocol)

        self._serializer = self.factory._serializers[serializerId]


class WampWebSocketFactory(object):
    """
    Base class for WAMP-over-WebSocket transport factory mixins.
    """

    def __init__(self, factory, serializers=None, debug_wamp=False):
        """
        Ctor.

        :param factory: A callable that produces instances that implement
           :class:`autobahn.wamp.interfaces.ITransportHandler`
        :type factory: callable
        :param serializers: A list of WAMP serializers to use (or None for default
           serializers). Serializers must implement
           :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializers: list
        """
        assert(callable(factory))
        self._factory = factory

        self.debug_wamp = debug_wamp

        if serializers is None:
            serializers = []

            # try MsgPack WAMP serializer
            try:
                from autobahn.wamp.serializer import MsgPackSerializer
                serializers.append(MsgPackSerializer(batched=True))
                serializers.append(MsgPackSerializer())
            except ImportError:
                pass

            # try JSON WAMP serializer
            try:
                from autobahn.wamp.serializer import JsonSerializer
                serializers.append(JsonSerializer(batched=True))
                serializers.append(JsonSerializer())
            except ImportError:
                pass

            if not serializers:
                raise Exception("could not import any WAMP serializers")

        self._serializers = {}
        for ser in serializers:
            self._serializers[ser.SERIALIZER_ID] = ser

        self._protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]


class WampWebSocketServerFactory(WampWebSocketFactory):
    """
    Mixin for WAMP-over-WebSocket server transport factories.
    """


class WampWebSocketClientFactory(WampWebSocketFactory):
    """
    Mixin for WAMP-over-WebSocket client transport factories.
    """
