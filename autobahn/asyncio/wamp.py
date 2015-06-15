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


def _create_tcp4_stream_transport(loop, apprunner, wamp_transport_factory, **kw):
    """
    The default callable used for _create_stream_transport in
    ApplicationRunner, this will parse the provided websocket URL and
    connect via TCP4 (with TLS if it's a `wss://` URL).
    """

    isSecure, host, port, resource, path, params = parseWsUrl(apprunner.url)

    if apprunner.ssl is None:
        ssl = isSecure
    else:
        if apprunner.ssl and not isSecure:
            raise RuntimeError(
                'ssl argument value passed to %s conflicts with the "ws:" '
                'prefix of the url argument. Did you mean to use "wss:"?' %
                apprunner.__class__.__name__)
        ssl = apprunner.ssl

    coro = loop.create_connection(wamp_transport_factory, host, port, ssl=ssl)
    return asyncio.async(coro)


def _create_unix_stream_transport(loop, apprunner, wamp_transport_factory, **kw):
    """
    Connects to a Unix socket as the transport. You must pass the
    socket path as `socket_path=` kwarg to `ApplicationRunner.run()`
    """

    try:
        socket_path = kw['socket_path']
    except KeyError:
        raise RuntimeError("Pass socket_path= kwarg to ApplicationRunner.run()")

    url = None  # see autobahn.websocket.protocol.WebSocketClientFactory

    if apprunner.ssl is not None:
        raise RuntimeError('ssl= argument inconsistent with Unix-domain sockets')

    coro = loop.create_unix_connection(wamp_transport_factory, socket_path)
    return asyncio.async(coro)


def _create_websocket_wamp_factory(reactor, apprunner, session_factory, **kw):
    # factory for using ApplicationSession
    def create():
        cfg = ComponentConfig(apprunner.realm, apprunner.extra)
        try:
            session = session_factory(cfg)
        except Exception as e:
            print(e)
            asyncio.get_event_loop().stop()
        else:
            session.debug_app = apprunner.debug_app
            return session

    return WampWebSocketClientFactory(
        create, url=apprunner.url, serializers=apprunner.serializers,
        debug=apprunner.debug, debug_wamp=apprunner.debug_wamp
    )


class ApplicationRunner(object):
    """
    This class is a convenience tool mainly for development and quick hosting
    of WAMP application components.

    It can host a WAMP application component in a WAMP-over-WebSocket client
    connecting to a WAMP router.
    """

    def __init__(self, url, realm, extra=None, serializers=None,
                 debug=False, debug_wamp=False, debug_app=False,
                 ssl=None,
                 _create_stream_transport=None, _create_wamp_factory=None):
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

        :param _create_stream_transport:
            A callable that takes two arguments `(apprunner,
            wamp_transport_factory)` and must accept any
            `kwargs`. Should be a coroutine or return a Future that fires with a
            connected protocol.

            Any kwargs passed to ApplicationRunner.run() are passed on
            to this method.

            **NOTE**: This API is currently in flux and may change,
            hence the leading underscore. However, this allows
            flexibility in creating the underlying transport.

            Currently the following options are provided:

            - `None`: (the default) creates a TCP4 (optionally with
              TLS) transport unless `url` is None, in which case a
              UNIX transport is created instead

            - `_create_unix_stream_transport`: creates a Unix-socket
              connection (needs `socket_path=` passed to run())
        :type _create_stream_transport: callable

        :param _create_wamp_factory:
            A callable that takes the ApplicationRunner instance and a
            session-creation method (e.g. ApplicationSession) and
            returns a new transport factory. This is subsequently passed to the
            `_create_stream_transport` callable. For Twisted this must
            implement :tx:`twisted.internet.interfaces.IProtocolFactory`.
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
        self._create_stream_transport = _create_stream_transport or _create_tcp4_stream_transport
        # since a None URL is used by autobahn.websocket.protocol.WebSocketClientFactory
        if _create_stream_transport is None and url is None:
            self._create_stream_transport = _create_unix_stream_transport
        self._create_wamp_factory = _create_wamp_factory or _create_websocket_wamp_factory

    def run(self, make, **kw):
        """
        Run the application component.

        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable
        """

        # set up the event-loop and ensure txaio is using the same one
        loop = asyncio.get_event_loop()
        txaio.use_asyncio()
        txaio.config.loop = loop

        # want to shut down nicely on TERM
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

        # create our connection; this is some WAMP dialect over an
        # underlying stream transport.
        transport_factory = self._create_wamp_factory(loop, self, make, **kw)
        d = self._create_stream_transport(loop, self, transport_factory, **kw)
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
