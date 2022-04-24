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

import copy
import traceback

from typing import Optional, Dict, Tuple

from autobahn.websocket import protocol
from autobahn.websocket.types import ConnectionDeny, ConnectionRequest, ConnectionResponse
from autobahn.wamp.types import TransportDetails
from autobahn.wamp.interfaces import ITransport, ISession
from autobahn.wamp.exception import ProtocolError, SerializationError, TransportLost

__all__ = ('WampWebSocketServerProtocol',
           'WampWebSocketClientProtocol',
           'WampWebSocketServerFactory',
           'WampWebSocketClientFactory')


class WampWebSocketProtocol(object):
    """
    Base class for WAMP-over-WebSocket transport mixins.
    """

    _session: Optional[ISession] = None  # default; self.session is set in onOpen
    _transport_details: Optional[TransportDetails] = None

    def _bailout(self, code: int, reason: Optional[str] = None):
        self.log.debug('Failing WAMP-over-WebSocket transport: code={code}, reason="{reason}"', code=code,
                       reason=reason)
        self._fail_connection(code, reason)

    def onOpen(self):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`
        """
        # WebSocket connection established. Now let the user WAMP session factory
        # create a new WAMP session and fire off session open callback.
        try:
            self._session = self.factory._factory()
            self._session._transport = self
            self._session.onOpen(self)
        except Exception as e:
            self.log.critical("{tb}", tb=traceback.format_exc())
            reason = 'WAMP Internal Error ({0})'.format(e)
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason=reason)

    def onClose(self, wasClean: bool, code: int, reason: Optional[str]):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`
        """
        # WAMP session might never have been established in the first place .. guard this!
        self._onclose_reason = reason
        if self._session is not None:
            # WebSocket connection lost - fire off the WAMP
            # session close callback
            # noinspection PyBroadException
            try:
                self.log.debug(
                    'WAMP-over-WebSocket transport lost: wasClean={wasClean}, code={code}, reason="{reason}"',
                    wasClean=wasClean, code=code, reason=reason)
                self._session.onClose(wasClean)
            except Exception:
                self.log.critical("{tb}", tb=traceback.format_exc())
            self._session = None

    def onMessage(self, payload: bytes, isBinary: bool):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`
        """
        try:
            for msg in self._serializer.unserialize(payload, isBinary):
                self.log.trace(
                    "WAMP RECV: message={message}, session={session}, authid={authid}",
                    authid=self._session._authid,
                    session=self._session._session_id,
                    message=msg,
                )
                self._session.onMessage(msg)

        except ProtocolError as e:
            self.log.critical("{tb}", tb=traceback.format_exc())
            reason = 'WAMP Protocol Error ({0})'.format(e)
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, reason=reason)

        except Exception as e:
            self.log.critical("{tb}", tb=traceback.format_exc())
            reason = 'WAMP Internal Error ({0})'.format(e)
            self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason=reason)

    def send(self, msg):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.send`
        """
        if self.isOpen():
            try:
                self.log.trace(
                    "WAMP SEND: message={message}, session={session}, authid={authid}",
                    authid=self._session._authid,
                    session=self._session._session_id,
                    message=msg,
                )
                payload, isBinary = self._serializer.serialize(msg)
            except Exception as e:
                self.log.error("WAMP message serialization error: {}".format(e))
                # all exceptions raised from above should be serialization errors ..
                raise SerializationError("WAMP message serialization error: {0}".format(e))
            else:
                self.sendMessage(payload, isBinary)
        else:
            raise TransportLost()

    def isOpen(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.isOpen`
        """
        return self._session is not None

    @property
    def transport_details(self) -> Optional[TransportDetails]:
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.transport_details`
        """
        return self._transport_details

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


def parseSubprotocolIdentifier(subprotocol: str) -> Tuple[Optional[int], Optional[str]]:
    try:
        s = subprotocol.split('.')
        if s[0] != 'wamp':
            raise Exception('WAMP WebSocket subprotocol identifier must start with "wamp", not "{}"'.format(s[0]))
        version = int(s[1])
        serializer_id = '.'.join(s[2:])
        return version, serializer_id
    except:
        return None, None


class WampWebSocketServerProtocol(WampWebSocketProtocol):
    """
    Mixin for WAMP-over-WebSocket server transports.
    """

    STRICT_PROTOCOL_NEGOTIATION = True

    def onConnect(self, request: ConnectionRequest) -> Tuple[Optional[str], Dict[str, str]]:
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
        """
        headers = {}
        for subprotocol in request.protocols:
            version, serializerId = parseSubprotocolIdentifier(subprotocol)
            if version == 2 and serializerId in self.factory._serializers.keys():
                # copy over serializer form factory, so that we keep per-session serializer stats
                self._serializer = copy.copy(self.factory._serializers[serializerId])

                return subprotocol, headers

        if self.STRICT_PROTOCOL_NEGOTIATION:
            raise ConnectionDeny(ConnectionDeny.BAD_REQUEST, 'This server only speaks WebSocket subprotocols {}'.format(
                ', '.join(self.factory.protocols)))
        else:
            # assume wamp.2.json (but do not announce/select it)
            self._serializer = copy.copy(self.factory._serializers['json'])
            return None, headers


class WampWebSocketClientProtocol(WampWebSocketProtocol):
    """
    Mixin for WAMP-over-WebSocket client transports.
    """

    STRICT_PROTOCOL_NEGOTIATION = True

    def onConnect(self, response: ConnectionResponse):
        """
        Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
        """
        if response.protocol not in self.factory.protocols:
            if self.STRICT_PROTOCOL_NEGOTIATION:
                raise Exception('The server does not speak any of the WebSocket subprotocols {} we requested.'.format(
                    ', '.join(self.factory.protocols)))
            else:
                # assume wamp.2.json
                serializer_id = 'json'
        else:
            version, serializer_id = parseSubprotocolIdentifier(response.protocol)

        # copy over serializer form factory, so that we keep per-session serializer stats
        self._serializer = copy.copy(self.factory._serializers[serializer_id])


class WampWebSocketFactory(object):
    """
    Base class for WAMP-over-WebSocket transport factory mixins.
    """

    def __init__(self, factory, serializers=None):
        """

        :param factory: A callable that produces instances that implement
           :class:`autobahn.wamp.interfaces.ITransportHandler`
        :type factory: callable

        :param serializers: A list of WAMP serializers to use (or None for default
           serializers). Serializers must implement
           :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializers: list
        """
        if callable(factory):
            self._factory = factory
        else:
            self._factory = lambda: factory

        if serializers is None:
            serializers = []

            # try CBOR WAMP serializer
            try:
                from autobahn.wamp.serializer import CBORSerializer
                serializers.append(CBORSerializer(batched=True))
                serializers.append(CBORSerializer())
            except ImportError:
                pass

            # try MsgPack WAMP serializer
            try:
                from autobahn.wamp.serializer import MsgPackSerializer
                serializers.append(MsgPackSerializer(batched=True))
                serializers.append(MsgPackSerializer())
            except ImportError:
                pass

            # try UBJSON WAMP serializer
            try:
                from autobahn.wamp.serializer import UBJSONSerializer
                serializers.append(UBJSONSerializer(batched=True))
                serializers.append(UBJSONSerializer())
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
                raise Exception('Could not import any WAMP serializer')

        self._serializers = {}
        for ser in serializers:
            self._serializers[ser.SERIALIZER_ID] = ser

        self._protocols = ['wamp.2.{}'.format(ser.SERIALIZER_ID) for ser in serializers]


class WampWebSocketServerFactory(WampWebSocketFactory):
    """
    Mixin for WAMP-over-WebSocket server transport factories.
    """


class WampWebSocketClientFactory(WampWebSocketFactory):
    """
    Mixin for WAMP-over-WebSocket client transport factories.
    """
