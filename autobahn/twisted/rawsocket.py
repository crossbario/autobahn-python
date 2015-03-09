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
        ##
        try:
            peer = self.transport.getPeer()
        except AttributeError:
            # ProcessProtocols lack getPeer()
            self.peer = "?"
        else:
            self.peer = peer2str(peer)

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


class WampRawSocketClientProtocol(WampRawSocketProtocol):
    """
    Base class for Twisted-based WAMP-over-RawSocket client protocols.
    """


class WampRawSocketFactory(Factory):
    """
    Base class for Twisted-based WAMP-over-RawSocket factories.
    """

    def __init__(self, factory, serializer, debug=False):
        """

        :param factory: A callable that produces instances that implement
            :class:`autobahn.wamp.interfaces.ITransportHandler`
        :type factory: callable
        :param serializer: A WAMP serializer to use. A serializer must implement
            :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializer: obj
        """
        assert(callable(factory))
        self._factory = factory
        self._serializer = serializer
        self.debug = debug


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
