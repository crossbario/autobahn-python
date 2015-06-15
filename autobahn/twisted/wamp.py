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

import sys
import inspect

from twisted.python import log
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted.websocket import WampWebSocketClientFactory

import six
import txaio
txaio.use_twisted()


__all__ = [
    'ApplicationSession',
    'ApplicationSessionFactory',
    'ApplicationRunner',
    'Application',
    'Service'
]

try:
    from twisted.application import service
except (ImportError, SyntaxError):
    # Not on PY3 yet
    service = None
    __all__.pop(__all__.index('Service'))


class ApplicationSession(protocol.ApplicationSession):
    """
    WAMP application session for Twisted-based applications.
    """

    def onUserError(self, e, msg):
        """
        Override of wamp.ApplicationSession
        """
        # see docs; will print currently-active exception to the logs,
        # which is just what we want.
        log.err(e)
        # also log the framework-provided error-message
        log.err(msg)


class ApplicationSessionFactory(protocol.ApplicationSessionFactory):
    """
    WAMP application session factory for Twisted-based applications.
    """

    session = ApplicationSession
    """
   The application session class this application session factory will use. Defaults to :class:`autobahn.twisted.wamp.ApplicationSession`.
   """

def _create_tcp4_stream_transport(reactor, apprunner, wamp_transport_factory, **kw):
    """
    The default callable used for _create_stream_transport in
    ApplicationRunner, this will parse the provided websocket URL and
    connect via TCP4 (with TLS if it's a `wss://` URL).
    """

    isSecure, host, port, resource, path, params = parseWsUrl(apprunner.url)

    # if user passed ssl= but isn't using isSecure, we'll never use
    # the ssl argument which makes no sense.
    context_factory = None
    if apprunner.ssl is not None:
        if not isSecure:
            raise RuntimeError(
                'ssl= argument value passed to {0} conflicts with the "ws:" '
                'prefix of the url argument. Did you mean to use "wss:"?'.format(
                    apprunner.__class__.__name__)
            )
        context_factory = apprunner.ssl
    elif isSecure:
        from twisted.internet.ssl import optionsForClientTLS
        context_factory = optionsForClientTLS(six.u(host))

    if isSecure:
        from twisted.internet.endpoints import SSL4ClientEndpoint
        assert context_factory is not None
        client = SSL4ClientEndpoint(reactor, host, port, context_factory)
    else:
        from twisted.internet.endpoints import TCP4ClientEndpoint
        client = TCP4ClientEndpoint(reactor, host, port)

    return client.connect(wamp_transport_factory)


def _create_unix_stream_transport(reactor, apprunner, wamp_transport_factory, **kw):
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

    from twisted.internet.endpoints import UNIXClientEndpoint
    client = UNIXClientEndpoint(reactor, socket_path)
    return client.connect(wamp_transport_factory)


def _create_endpoint_stream_transport(reactor, apprunner, wamp_transport_factory, **kw):
    """
    Connects to any Twisted endpoint-string transport. You must pass
    an `endpoint=` kwarg to `ApplicationRunner.run()`
    """

    try:
        ep_string = kw['endpoint']
    except KeyError:
        raise RuntimeError("Must pass endpoint= kwarg to ApplicationRunner.run()")

    if apprunner.ssl is not None:
        raise RuntimeError('Cannot pass ssl= argument if using Twisted endpoints.')

    from twisted.internet.endpoints import clientFromString
    client = clientFromString(reactor, ep_string)
    return client.connect(wamp_transport_factory)


def _create_websocket_wamp_factory(reactor, apprunner, session_factory, **kw):
    # factory for using ApplicationSession
    def create():
        cfg = ComponentConfig(apprunner.realm, apprunner.extra)
        try:
            session = session_factory(cfg)
        except Exception as e:
            log.err("Exception while creating session: {0}".format(e))
            if 'start_reactor' in kw and kw['start_reactor']:
                log.err("Fatal, stopping reactor.")
                reactor.stop()
            raise
        else:
            session.debug_app = apprunner.debug_app
            return session

    return WampWebSocketClientFactory(
        create, url=apprunner.url,
        debug=apprunner.debug, debug_wamp=apprunner.debug_wamp
    )

class ApplicationRunner(object):
    """
    This class is a convenience tool mainly for development and quick hosting
    of WAMP application components.

    It can host a WAMP application component in a WAMP-over-WebSocket client
    connecting to a WAMP router.
    """

    def __init__(self, url, realm, extra=None, debug=False, debug_wamp=False, debug_app=False, ssl=None,
                 _create_stream_transport=None, _create_wamp_factory=None):
        """
        :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
        :type url: unicode

        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode

        :param extra: Optional extra configuration to forward to the application component.
        :type extra: dict

        :param debug: Turn on low-level debugging.
        :type debug: bool

        :param debug_wamp: Turn on WAMP-level debugging.
        :type debug_wamp: bool

        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool

        :param ssl: (Optional). If specified this should be an
            instance suitable to pass as ``sslContextFactory`` to
            :class:`twisted.internet.endpoints.SSL4ClientEndpoint`` such
            as :class:`twisted.internet.ssl.CertificateOptions`. Leaving
            it as ``None`` will use the result of calling Twisted's
            :meth:`twisted.internet.ssl.platformTrust` which tries to use
            your distribution's CA certificates.
        :type ssl: :class:`twisted.internet.ssl.CertificateOptions`

        :param _create_stream_transport:
            A callable that takes two arguments `(apprunner,
            wamp_transport_factory)` and must accept any
            `kwargs`. Should return a Deferred that fires with a
            connected `IProtocol`.

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

            - `_create_endpoint_stream_transport`: Uses Twisted's
              :tx:`twisted.internet.endpoints.clientFromString` parser
              to create the stream transport. Requires `endpoint=`
              passed to run().
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
        self.ssl = ssl
        self._create_stream_transport = _create_stream_transport or _create_tcp4_stream_transport
        # since a None URL is used by autobahn.websocket.protocol.WebSocketClientFactory
        if _create_stream_transport is None and url is None:
            self._create_stream_transport = _create_unix_stream_transport
        self._create_wamp_factory = _create_wamp_factory or _create_websocket_wamp_factory

    def run(self, make, start_reactor=True, **kw):
        """
        Run the application component.

        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable

        :param start_reactor: if True (the default) this method starts
           the Twisted reactor and doesn't return until the reactor
           stops. If there are any problems starting the reactor or
           connect()-ing, we stop the reactor and raise the exception
           back to the caller.

        Any additional kwargs are given to the underlying
        _create_stream_transport callable (see __init__ docs).

        :returns: None is returned, unless you specify
            ``start_reactor=False`` in which case the Deferred that
            connect() returns is returned; this will callback() with
            an IProtocol instance, which will actually be an instance
            of :class:`WampWebSocketClientProtocol`
        """
        from twisted.internet import reactor
        txaio.use_twisted()
        txaio.config.loop = reactor

        # start logging to console
        if self.debug or self.debug_wamp or self.debug_app:
            log.startLogging(sys.stdout)

        # create our connection; this is some WAMP dialect over an
        # underlying stream transport.
        # XXX what to do about start_reactor and error-handling on
        #     ApplicationSession creation? ugly to pass it here...
        transport_factory = self._create_wamp_factory(reactor, self, make, start_reactor=start_reactor)
        d = self._create_stream_transport(reactor, self, transport_factory, **kw)

        # as the reactor shuts down, we wish to wait until we've sent
        # out our "Goodbye" message; leave() returns a Deferred that
        # fires when the transport gets to STATE_CLOSED
        def cleanup(proto):
            if hasattr(proto, '_session') and proto._session is not None:
                return proto._session.leave()
        # if we connect successfully, the arg is a WampWebSocketClientProtocol
        d.addCallback(lambda proto: reactor.addSystemEventTrigger(
            'before', 'shutdown', cleanup, proto))

        # if the user didn't ask us to start the reactor, then they
        # get to deal with any connect errors themselves.
        if start_reactor:
            # if an error happens in the connect(), we save the underlying
            # exception so that after the event-loop exits we can re-raise
            # it to the caller.

            class ErrorCollector(object):
                exception = None

                def __call__(self, failure):
                    self.exception = failure.value
                    # print(failure.getErrorMessage())
                    reactor.stop()
            connect_error = ErrorCollector()
            d.addErrback(connect_error)

            # now enter the Twisted reactor loop
            reactor.run()

            # if we exited due to a connection error, raise that to the
            # caller
            if connect_error.exception:
                raise connect_error.exception

        else:
            # let the caller handle any errors
            return d


class _ApplicationSession(ApplicationSession):
    """
    WAMP application session class used internally with :class:`autobahn.twisted.app.Application`.
    """

    def __init__(self, config, app):
        """

        :param config: The component configuration.
        :type config: Instance of :class:`autobahn.wamp.types.ComponentConfig`
        :param app: The application this session is for.
        :type app: Instance of :class:`autobahn.twisted.wamp.Application`.
        """
        # noinspection PyArgumentList
        ApplicationSession.__init__(self, config)
        self.app = app

    @inlineCallbacks
    def onConnect(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`
        """
        yield self.app._fire_signal('onconnect')
        self.join(self.config.realm)

    @inlineCallbacks
    def onJoin(self, details):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onJoin`
        """
        for uri, proc in self.app._procs:
            yield self.register(proc, uri)

        for uri, handler in self.app._handlers:
            yield self.subscribe(handler, uri)

        yield self.app._fire_signal('onjoined')

    @inlineCallbacks
    def onLeave(self, details):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onLeave`
        """
        yield self.app._fire_signal('onleave')
        self.disconnect()

    @inlineCallbacks
    def onDisconnect(self):
        """
        Implements :func:`autobahn.wamp.interfaces.ISession.onDisconnect`
        """
        yield self.app._fire_signal('ondisconnect')


class Application(object):
    """
    A WAMP application. The application object provides a simple way of
    creating, debugging and running WAMP application components.
    """

    def __init__(self, prefix=None):
        """

        :param prefix: The application URI prefix to use for procedures and topics,
           e.g. ``"com.example.myapp"``.
        :type prefix: unicode
        """
        self._prefix = prefix

        # procedures to be registered once the app session has joined the router/realm
        self._procs = []

        # event handler to be subscribed once the app session has joined the router/realm
        self._handlers = []

        # app lifecycle signal handlers
        self._signals = {}

        # once an app session is connected, this will be here
        self.session = None

    def __call__(self, config):
        """
        Factory creating a WAMP application session for the application.

        :param config: Component configuration.
        :type config: Instance of :class:`autobahn.wamp.types.ComponentConfig`

        :returns: obj -- An object that derives of
           :class:`autobahn.twisted.wamp.ApplicationSession`
        """
        assert(self.session is None)
        self.session = _ApplicationSession(config, self)
        return self.session

    def run(self, url=u"ws://localhost:8080/ws", realm=u"realm1",
            debug=False, debug_wamp=False, debug_app=False,
            start_reactor=True):
        """
        Run the application.

        :param url: The URL of the WAMP router to connect to.
        :type url: unicode
        :param realm: The realm on the WAMP router to join.
        :type realm: unicode
        :param debug: Turn on low-level debugging.
        :type debug: bool
        :param debug_wamp: Turn on WAMP-level debugging.
        :type debug_wamp: bool
        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool
        """
        runner = ApplicationRunner(url, realm,
                                   debug=debug, debug_wamp=debug_wamp, debug_app=debug_app)
        runner.run(self.__call__, start_reactor)

    def register(self, uri=None):
        """
        Decorator exposing a function as a remote callable procedure.

        The first argument of the decorator should be the URI of the procedure
        to register under.

        :Example:

        .. code-block:: python

           @app.register('com.myapp.add2')
           def add2(a, b):
              return a + b

        Above function can then be called remotely over WAMP using the URI `com.myapp.add2`
        the function was registered under.

        If no URI is given, the URI is constructed from the application URI prefix
        and the Python function name.

        :Example:

        .. code-block:: python

           app = Application('com.myapp')

           # implicit URI will be 'com.myapp.add2'
           @app.register()
           def add2(a, b):
              return a + b

        If the function `yields` (is a co-routine), the `@inlineCallbacks` decorator
        will be applied automatically to it. In that case, if you wish to return something,
        you should use `returnValue`:

        :Example:

        .. code-block:: python

           from twisted.internet.defer import returnValue

           @app.register('com.myapp.add2')
           def add2(a, b):
              res = yield stuff(a, b)
              returnValue(res)

        :param uri: The URI of the procedure to register under.
        :type uri: unicode
        """
        def decorator(func):
            if uri:
                _uri = uri
            else:
                assert(self._prefix is not None)
                _uri = "{0}.{1}".format(self._prefix, func.__name__)

            if inspect.isgeneratorfunction(func):
                func = inlineCallbacks(func)

            self._procs.append((_uri, func))
            return func
        return decorator

    def subscribe(self, uri=None):
        """
        Decorator attaching a function as an event handler.

        The first argument of the decorator should be the URI of the topic
        to subscribe to. If no URI is given, the URI is constructed from
        the application URI prefix and the Python function name.

        If the function yield, it will be assumed that it's an asynchronous
        process and inlineCallbacks will be applied to it.

        :Example:

        .. code-block:: python

           @app.subscribe('com.myapp.topic1')
           def onevent1(x, y):
              print("got event on topic1", x, y)

        :param uri: The URI of the topic to subscribe to.
        :type uri: unicode
        """
        def decorator(func):
            if uri:
                _uri = uri
            else:
                assert(self._prefix is not None)
                _uri = "{0}.{1}".format(self._prefix, func.__name__)

            if inspect.isgeneratorfunction(func):
                func = inlineCallbacks(func)

            self._handlers.append((_uri, func))
            return func
        return decorator

    def signal(self, name):
        """
        Decorator attaching a function as handler for application signals.

        Signals are local events triggered internally and exposed to the
        developer to be able to react to the application lifecycle.

        If the function yield, it will be assumed that it's an asynchronous
        coroutine and inlineCallbacks will be applied to it.

        Current signals :

           - `onjoined`: Triggered after the application session has joined the
              realm on the router and registered/subscribed all procedures
              and event handlers that were setup via decorators.
           - `onleave`: Triggered when the application session leaves the realm.

        .. code-block:: python

           @app.signal('onjoined')
           def _():
              # do after the app has join a realm

        :param name: The name of the signal to watch.
        :type name: unicode
        """
        def decorator(func):
            if inspect.isgeneratorfunction(func):
                func = inlineCallbacks(func)
            self._signals.setdefault(name, []).append(func)
            return func
        return decorator

    @inlineCallbacks
    def _fire_signal(self, name, *args, **kwargs):
        """
        Utility method to call all signal handlers for a given signal.

        :param name: The signal name.
        :type name: str
        """
        for handler in self._signals.get(name, []):
            try:
                # FIXME: what if the signal handler is not a coroutine?
                # Why run signal handlers synchronously?
                yield handler(*args, **kwargs)
            except Exception as e:
                # FIXME
                log.msg("Warning: exception in signal handler swallowed", e)


if service:
    # Don't define it if Twisted's service support isn't here

    class Service(service.MultiService):
        """
        A WAMP application as a twisted service.
        The application object provides a simple way of creating, debugging and running WAMP application
        components inside a traditional twisted application

        This manages application lifecycle of the wamp connection using startService and stopService
        Using services also allows to create integration tests that properly terminates their connections

        It can host a WAMP application component in a WAMP-over-WebSocket client
        connecting to a WAMP router.
        """
        factory = WampWebSocketClientFactory

        def __init__(self, url, realm, make, extra=None,
                     debug=False, debug_wamp=False, debug_app=False):
            """

            :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
            :type url: unicode
            :param realm: The WAMP realm to join the application session to.
            :type realm: unicode
            :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
               when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
            :type make: callable
            :param extra: Optional extra configuration to forward to the application component.
            :type extra: dict
            :param debug: Turn on low-level debugging.
            :type debug: bool
            :param debug_wamp: Turn on WAMP-level debugging.
            :type debug_wamp: bool
            :param debug_app: Turn on app-level debugging.
            :type debug_app: bool

            You can replace the attribute factory in order to change connectionLost or connectionFailed behaviour.
            The factory attribute must return a WampWebSocketClientFactory object
            """
            self.url = url
            self.realm = realm
            self.extra = extra or dict()
            self.debug = debug
            self.debug_wamp = debug_wamp
            self.debug_app = debug_app
            self.make = make
            service.MultiService.__init__(self)
            self.setupService()

        def setupService(self):
            """
            Setup the application component.
            """
            isSecure, host, port, resource, path, params = parseWsUrl(self.url)

            # factory for use ApplicationSession
            def create():
                cfg = ComponentConfig(self.realm, self.extra)
                session = self.make(cfg)
                session.debug_app = self.debug_app
                return session

            # create a WAMP-over-WebSocket transport client factory
            transport_factory = self.factory(create, url=self.url,
                                             debug=self.debug, debug_wamp=self.debug_wamp)

            # setup the client from a Twisted endpoint

            if isSecure:
                from twisted.application.internet import SSLClient
                clientClass = SSLClient
            else:
                from twisted.application.internet import TCPClient
                clientClass = TCPClient

            client = clientClass(host, port, transport_factory)
            client.setServiceParent(self)
