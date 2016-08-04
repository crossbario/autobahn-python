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

import six

from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
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
    The application session class this application session factory will use.
    Defaults to :class:`autobahn.asyncio.wamp.ApplicationSession`.
    """


class ApplicationRunner(object):
    """
    This class is a convenience tool mainly for development and quick hosting
    of WAMP application components.

    It can host a WAMP application component in a WAMP-over-WebSocket client
    connecting to a WAMP router.
    """

    def __init__(self, url, realm, extra=None, serializers=None, ssl=None):
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

        :param ssl: An (optional) SSL context instance or a bool. See
           the documentation for the `loop.create_connection` asyncio
           method, to which this value is passed as the ``ssl=``
           kwarg.
        :type ssl: :class:`ssl.SSLContext` or bool
        """
        assert(type(url) == six.text_type)
        assert(type(realm) == six.text_type)
        assert(extra is None or type(extra) == dict)
        self.url = url
        self.realm = realm
        self.extra = extra or dict()
        self.serializers = serializers
        self.ssl = ssl

    def ssl_check(self, isSecure=None):
        """
        Check the ssl parameters to avoid conflicting values and return it.

        :param isSecure: value extracted from url.

        :returns: :class:`ssl.SSLContext` or bool -- An (optional) SSL context
           instance or a bool. See the documentation for the
           `loop.create_connection` asyncio method, to which this value is
           passed as the ``ssl=`` kwarg.

        """
        ssl = None
        if self.ssl is None:
            ssl = isSecure
        else:
            if self.ssl and not isSecure:
                raise RuntimeError(
                    'ssl argument value passed to %s conflicts with the "ws:" '
                    'prefix of the url argument. Did you mean to use "wss:"?' %
                    self.__class__.__name__)
            ssl = self.ssl
        return ssl

    def create_endpoint(self, make, loop):
        """
        Create the wamp endpoint to interact with the component.

        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :param loop: The event loop instance that runs the component
        :type make: callable
        :type loop: :class:`asyncio.BaseEventLoop`

        :returns: :class:`asyncio.coroutine` -- the coroutine that creates the
           transport and the wamp protocol
        """
        self.loop = loop

        # 1) factory for use ApplicationSession
        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = make(cfg)
            except Exception:
                self.log.failure("App session could not be created! ")
                raise
            else:
                return session

        isSecure, host, port, resource, path, params = parse_url(self.url)

        ssl = self.ssl_check(isSecure)

        # 2) create a WAMP-over-WebSocket transport client factory
        transport_factory = WampWebSocketClientFactory(create, url=self.url, serializers=self.serializers)

        txaio.use_asyncio()
        # start logging
        txaio.start_logging(level='info')
        txaio.config.loop = self.loop
        coro = self.loop.create_connection(transport_factory, host, port,
                                           ssl=ssl)
        return(coro)

    def cleanup(self, protocol, loop):
        """
        Send a goodbye message if there is still a session.

        :param protocol: An instance of :class:`autobahn.wamp.protocol.ApplicationSession`
        :param loop: An instance of :class:`asyncio.BaseEventLoop`
        """

        if protocol._session:
            loop.run_until_complete(protocol._session.leave())

    def run(self, make):
        """
        Run the application component.

        :param make: A factory that produces instances of
                     :class:`autobahn.asyncio.wamp.ApplicationSession` when
                     called with an instance of
                     :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable
        """
        loop = asyncio.get_event_loop()
        connect_coro = self.create_endpoint(make, loop)
        (transport, protocol) = loop.run_until_complete(connect_coro)

        try:
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except NotImplementedError:
            # signals are not available on Windows
            pass

        # 4) now enter the asyncio event loop
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            # wait until we send Goodbye if user hit ctrl-c
            # (done outside this except so SIGTERM gets the same handling)
            pass

        # give Goodbye message a chance to go through, if we still
        # have an active session
        self.cleanup(protocol, loop)
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
        loop.close()
