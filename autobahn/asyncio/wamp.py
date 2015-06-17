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
import signal

from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.protocol import parseWsUrl
from autobahn.asyncio.websocket import WampWebSocketClientFactory

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed to asyncio
    # noinspection PyUnresolvedReferences
    import trollius as asyncio

import txaio
txaio.use_asyncio()

__all__ = (
    'ApplicationSession',
    'ApplicationSessionFactory',
    'ApplicationRunner'
)


class ApplicationSession(protocol.ApplicationSession):
    """
    WAMP application session for asyncio-based applications.
    """


class ApplicationSessionFactory(protocol.ApplicationSessionFactory):
    """
    WAMP application session factory for asyncio-based applications.
    """

    session = ApplicationSession
    """
   The application session class this application session factory will use. Defaults to :class:`autobahn.asyncio.wamp.ApplicationSession`.
   """


class ApplicationRunner(object):
    """
    This class is a convenience tool mainly for development and quick hosting
    of WAMP application components.

    It can host a WAMP application component in a WAMP-over-WebSocket client
    connecting to a WAMP router.
    """

    def __init__(self, url, realm, extra=None, serializers=None,
                 debug=False, debug_wamp=False, debug_app=False,
                 ssl=None, socket_path=None):
        """
        :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
        :type url: unicode

        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode

        :param extra: Optional extra configuration to forward to the application component.
        :type extra: dict

        :param serializers: A list of WAMP serializers to use (or None for default serializers).
           Serializers must implement :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializers: list

        :param debug: Turn on low-level debugging.
        :type debug: bool

        :param debug_wamp: Turn on WAMP-level debugging.
        :type debug_wamp: bool

        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool

        :param ssl: An (optional) SSL context instance or a bool. See
           the documentation for the `loop.create_connection` asyncio
           method, to which this value is passed as the ``ssl=``
           kwarg.
        :type ssl: :class:`ssl.SSLContext` or bool
        """
        self.url = url
        self.realm = realm
        self.extra = extra or dict()
        self.debug = debug
        self.debug_wamp = debug_wamp
        self.debug_app = debug_app
        self.make = None
        self.serializers = serializers
        self.ssl = ssl
        self._socket_path = socket_path

        # configure our internal helpers for creating stream and WAMP
        # transports
        self._create_stream_transport = self._create_tcp4_stream_transport
        # since a None URL is used by autobahn.websocket.protocol.WebSocketClientFactory
        if url is None:
            if socket_path is None:
                raise RuntimeError("Must pass socket_path= kwarg if url is None")
            self._create_stream_transport = self._create_unix_stream_transport
        self._create_wamp_factory = self._create_websocket_wamp_factory

    def run(self, make):
        """
        Run the application component.

        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable

        :param socket_path: If you passed None as the URL, you must
            pass socket_path= to tell ApplicationRunner where your
            unix-socket is.
        :type socket_path: unicode
        """

        # set up the event-loop and ensure txaio is using the same one
        loop = asyncio.get_event_loop()
        txaio.use_asyncio()
        txaio.config.loop = loop

        # want to shut down nicely on TERM
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

        # create our connection; this is some WAMP dialect over an
        # underlying stream transport.
        transport_factory = self._create_wamp_factory(loop, make)
        d = self._create_stream_transport(loop, transport_factory)
        (transport, protocol) = loop.run_until_complete(d)

        # now enter the asyncio event loop
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            # wait until we send Goodbye if user hit ctrl-c
            # (done outside this except so SIGTERM gets the same handling)
            pass

        # if we still have a session hanging around, give it a chance
        # to disconnect properly.
        if hasattr(protocol, '_session') and protocol._session:
            loop.run_until_complete(protocol._session.leave())

        # exit
        loop.close()


    def _create_tcp4_stream_transport(self, loop, wamp_transport_factory):
        """
        Internal helper.

        Creates a TCP4 (possibly with TLS) stream transport.
        """

        isSecure, host, port, resource, path, params = parseWsUrl(self.url)

        if self.ssl is None:
            ssl = isSecure
        else:
            if self.ssl and not isSecure:
                raise RuntimeError(
                    'ssl argument value passed to %s conflicts with the "ws:" '
                    'prefix of the url argument. Did you mean to use "wss:"?' %
                    self.__class__.__name__)
            ssl = self.ssl

        coro = loop.create_connection(wamp_transport_factory, host, port, ssl=ssl)
        return asyncio.async(coro)


    def _create_unix_stream_transport(self, loop, wamp_transport_factory):
        """
        Internal helper.

        Creates a Unix socket as the stream transport.
        """

        url = None  # see autobahn.websocket.protocol.WebSocketClientFactory

        if self.ssl is not None:
            raise RuntimeError('ssl= argument inconsistent with Unix-domain sockets')

        coro = loop.create_unix_connection(wamp_transport_factory, self._socket_path)
        return asyncio.async(coro)


    def _create_websocket_wamp_factory(self, loop, session_factory, **kw):
        # factory for using ApplicationSession
        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = session_factory(cfg)
            except Exception as e:
                print(e)
                asyncio.get_event_loop().stop()
            else:
                session.debug_app = self.debug_app
                return session

        return WampWebSocketClientFactory(
            create, url=self.url, serializers=self.serializers,
            debug=self.debug, debug_wamp=self.debug_wamp
        )
