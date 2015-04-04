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

import binascii

from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.error import ConnectionDone

from autobahn.twisted.util import peer2str
from autobahn.wamp.exception import ProtocolError, SerializationError, TransportLost

__all__ = (
    'WampRawSocketServerProtocol',
    'WampRawSocketClientProtocol',
    'WampRawSocketServerFactory',
    'WampRawSocketClientFactory'
)


class WampRawSocketProtocol(Int32StringReceiver):
    """
    Base class for Twisted-based WAMP-over-RawSocket protocols.
    """

    def connectionMade(self):
        if self.factory.debug:
            log.msg("WAMP-over-RawSocket connection made")

        # the peer we are connected to
        #
        try:
            peer = self.transport.getPeer()
        except AttributeError:
            # ProcessProtocols lack getPeer()
            self.peer = "?"
        else:
            self.peer = peer2str(peer)

        # this will hold an ApplicationSession object
        # once the RawSocket opening handshake has been
        # completed
        #
        self._session = None

        self._serializer = None

        self._handshake_complete = False

        self._handshake_bytes = b''

    def _on_handshake_complete(self):
        try:
            self._session = self.factory._factory()
            self._session.onOpen(self)
        except Exception as e:
            # Exceptions raised in onOpen are fatal ..
            if self.factory.debug:
                log.msg("ApplicationSession constructor / onOpen raised ({0})".format(e))
            self.abort()

    def connectionLost(self, reason):
        if self.factory.debug:
            log.msg("WAMP-over-RawSocket connection lost: reason = '{0}'".format(reason))
        try:
            wasClean = isinstance(reason.value, ConnectionDone)
            self._session.onClose(wasClean)
        except Exception as e:
            # silently ignore exceptions raised here ..
            if self.factory.debug:
                log.msg("ApplicationSession.onClose raised ({0})".format(e))
        self._session = None

    def stringReceived(self, payload):
        if self.factory.debug:
            log.msg("RX octets: {0}".format(binascii.hexlify(payload)))
        try:
            for msg in self.factory._serializer.unserialize(payload):
                if self.factory.debug:
                    log.msg("RX WAMP message: {0}".format(msg))
                self._session.onMessage(msg)

        except ProtocolError as e:
            if self.factory.debug:
                log.msg("WAMP Protocol Error ({0}) - aborting connection".format(e))
            self.abort()

        except Exception as e:
            if self.factory.debug:
                log.msg("WAMP Internal Error ({0}) - aborting connection".format(e))
            self.abort()

    def send(self, msg):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.send`
        """
        if self.isOpen():
            if self.factory.debug:
                log.msg("TX WAMP message: {0}".format(msg))
            try:
                payload, _ = self.factory._serializer.serialize(msg)
            except Exception as e:
                # all exceptions raised from above should be serialization errors ..
                raise SerializationError("Unable to serialize WAMP application payload ({0})".format(e))
            else:
                self.sendString(payload)
                if self.factory.debug:
                    log.msg("TX octets: {0}".format(binascii.hexlify(payload)))
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
            self.transport.loseConnection()
        else:
            raise TransportLost()

    def abort(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransport.abort`
        """
        if self.isOpen():
            if hasattr(self.transport, 'abortConnection'):
                # ProcessProtocol lacks abortConnection()
                self.transport.abortConnection()
            else:
                self.transport.loseConnection()
        else:
            raise TransportLost()


class WampRawSocketServerProtocol(WampRawSocketProtocol):
    """
    Base class for Twisted-based WAMP-over-RawSocket server protocols.
    """

    def dataReceived(self, data):
        if self._handshake_complete:
            WampRawSocketProtocol.dataReceived(self, data)
        else:
            remaining = 4 - len(self._handshake_bytes)
            self._handshake_bytes += data[:remaining]

            if len(self._handshake_bytes) == 4:

                if self.factory.debug:
                    print("RawSocket opening handshake received: {0}".format(binascii.b2a_hex(self._handshake_bytes)))

                if ord(self._handshake_bytes[0]) != 0x7f:
                    if self.factory.debug:
                        print("Invalid magic byte (octet 1) in RawSocket opening handshake: was 0x{0}, but expected 0x7f".format(binascii.b2a_hex(self._handshake_bytes[0])))
                    self.abort()

                # peer requests us to send messages of maximum length 2**max_len_exp
                #
                max_len_exp = 9 + (ord(self._handshake_bytes[1]) >> 4)

                # client wants to speak this serialization format
                #
                ser_id = ord(self._handshake_bytes[1]) & 0x0F
                if ser_id in self.factory._serializers:
                    self._serializer = self.factory._serializers[ser_id]
                else:
                    if self.factory.debug:
                        print("RawSocket opening handshake - no suitable serializer found (client requested {0}, and we have {1})".format(ser_id, self.factory._serializers.keys()))
                    self.abort()

                # we request the peer to send message of maximum length 2**reply_max_len_exp
                #
                reply_max_len_exp = 24

                # send out handshake reply
                #
                reply_octet2 = chr(((reply_max_len_exp - 9) << 4) | self._serializer.RAWSOCKET_SERIALIZER_ID)
                self.transport.write(b'\x7F') # magic byte
                self.transport.write(reply_octet2) # max length / serializer
                self.transport.write(b'\x00\x00') # reserved octets

                self._handshake_complete = True
                self._on_handshake_complete()

            # consume any remaining data received already ..
            #
            data = data[remaining:]
            if data:
                self.dataReceived(data)


class WampRawSocketClientProtocol(WampRawSocketProtocol):
    """
    Base class for Twisted-based WAMP-over-RawSocket client protocols.
    """


class WampRawSocketFactory(Factory):
    """
    Base class for Twisted-based WAMP-over-RawSocket factories.
    """

    def __init__(self, factory, serializers=None, debug=False):
        """

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

        self.debug = debug
        self.debug = True

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
            self._serializers[ser.RAWSOCKET_SERIALIZER_ID] = ser


class WampRawSocketServerFactory(WampRawSocketFactory):
    """
    Base class for Twisted-based WAMP-over-RawSocket server factories.
    """
    protocol = WampRawSocketServerProtocol


class WampRawSocketClientFactory(WampRawSocketFactory):
    """
    Base class for Twisted-based WAMP-over-RawSocket client factories.
    """
    protocol = WampRawSocketClientProtocol
