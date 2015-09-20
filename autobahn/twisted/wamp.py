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

import six
import sys
import inspect

from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from twisted.internet.error import ReactorAlreadyRunning, ReactorNotRunning
from twisted.internet.interfaces import IStreamClientEndpoint, IProtocolFactory, IReactorCore
from twisted.internet.endpoints import clientFromString, UNIXClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint

try:
    _TLS = True
    from twisted.internet.endpoints import SSL4ClientEndpoint
    from twisted.internet.ssl import optionsForClientTLS, CertificateOptions
    from twisted.internet.interfaces import IOpenSSLClientConnectionCreator
except ImportError:
    _TLS = False

from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.twisted.rawsocket import WampRawSocketClientFactory
from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.wamp.runner import _ApplicationRunner, Connection

import txaio
txaio.use_twisted()


__all__ = [
    'ApplicationSession',
    'ApplicationSessionFactory',
    'ApplicationRunner',
    'Connection',
    'connect_to',
    'Application',
    'Service',
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


class ApplicationSessionFactory(protocol.ApplicationSessionFactory):
    """
    WAMP application session factory for Twisted-based applications.
    """

    session = ApplicationSession
    """
    The application session class this application session factory
    will use. Defaults to :class:`autobahn.twisted.wamp.ApplicationSession`.
    """


def _connect_stream(reactor, config, wamp_transport_factory, hostname=None):
    """
    Internal helper.

    Connects the given wamp_transport_factory to a stream endpoint, as
    determined from the config that's passed in (which should be just the
    "endpoint" part).

    NOTE this presumes that 'config' has already been checked with
    :meth:`autobahn.wamp.transport.check`

    hostname is only used if the 'tls' option is True

    Returns Deferred that fires with IProtocol
    """
    if reactor is None:
        from twisted.internet import reactor

    if isinstance(config, (str, six.text_type)):
        endpoint = clientFromString(reactor, config)

    elif IStreamClientEndpoint.providedBy(config):
        endpoint = IStreamClientEndpoint(config)

    else:
        if config['type'] == 'tcp':
            version = int(config.get('version', 4))
            host = str(config['host'])
            port = int(config['port'])
            timeout = int(config.get('timeout', 10))  # in seconds

            tls = config.get('tls', None)
            if tls is False:
                tls = None
            if tls:
                if not _TLS:
                    raise Exception('TLS configured, but no support'
                                    ' (is pyOpenSSL installed?)')
                # we accept Twisted objects here. This must be a
                # IOpenSSLClientConnectionCreator provider -- as
                # created, e.g., by
                # twisted.internet.ssl.optionsForClientTLS() or a
                # CertificateOptions instance
                if IOpenSSLClientConnectionCreator.providedBy(tls):
                    context = IOpenSSLClientConnectionCreator(tls)
                elif isinstance(tls, CertificateOptions):
                    context = tls
                elif tls is True:
                    context = optionsForClientTLS(hostname)
                else:
                    raise Exception("Unknown 'tls' option type '{}'".format(type(tls)))

                if version == 4:
                    endpoint = SSL4ClientEndpoint(
                        reactor,
                        host,
                        port,
                        context,
                        timeout=timeout,
                    )
                elif version == 6:
                    raise Exception("TLS on IPv6 not implemented")
                else:
                    raise Exception("invalid TCP protocol version {}".format(version))

            else:
                if version == 4:
                    creator = TCP4ClientEndpoint
                elif version == 6:
                    try:
                        from twisted.internet.endpoints import TCP6ClientEndpoint
                    except ImportError:
                        raise Exception("No TCP6 support; upgrade Twisted")
                    creator = TCP6ClientEndpoint
                else:
                    raise Exception("invalid TCP protocol version {}".format(version))
                endpoint = creator(reactor,
                                   host,
                                   port,
                                   timeout=timeout)

        elif config['type'] == 'unix':
            path = config['path']
            timeout = int(config.get('timeout', 10))  # in seconds
            endpoint = UNIXClientEndpoint(reactor, path, timeout=timeout)

        else:
            raise Exception("invalid endpoint type '{}'".format(config['type']))

        return endpoint.connect(wamp_transport_factory)


# needs custom asycio vs Twisted (because where the imports come from)
# -- or would have to do "if txaio.using_twisted():" etc switch-type
# statement.
def _create_wamp_factory(reactor, cfg, session_factory):
    """
    Internal helper.

    This creates the appropriate protocol-factory (that implements
    tx:`IProtocolFactory <twisted.internet.interfaces.IProtocolFactory>`)
    """

    # type in ['websocket', 'rawsocket']
    kind = cfg.get('type', 'websocket')

    if kind == 'websocket':
        return WampWebSocketClientFactory(
            session_factory, url=cfg['url'],
        )
    elif kind == 'rawsocket':
        return WampRawSocketClientFactory(
            session_factory,
        )
    else:
        raise RuntimeError("Unknown WAMP type '{}'".format(kind))


# XXX THINK move to transport.py?
# XXX the shutdown hooks being different between asyncio/twisted makes this hard to be generic :(
@inlineCallbacks
def connect_to(transport_config, session, loop=None):
    """:param reactor: the reactor to use (or None for default)

    :param transport_config: dict containing valid client transport
    config (see :mod:`autobahn.wamp.transport`) XXX maybe this should
    just demand an actual Factory? or accept either a dict (==config)
    or an IFactory provider? (to be consistent with asking for a
    straight ISession, instead of config)

    :param session: an ISession (e.g. ApplicationSession subclass)

    :returns: Deferred that callbacks with a protocol instance after a
    connection has been made (not necessarily a WAMP session joined
    yet, however)

    """

    def create():
        return session

    reactor = loop
    if loop is None:
        from twisted.internet import reactor

    if IProtocolFactory.providedBy(transport_config):
        transport_factory = transport_config
    else:
        transport_factory = _create_wamp_factory(reactor, transport_config, create)

    _, host, port, _, _, _ = parseWsUrl(transport_config['url'])
    if 'endpoint' in transport_config:
        endpoint = transport_config['endpoint']
    else:
        endpoint = dict(host=host, port=port, type='tcp', version=4)
    proto = yield _connect_stream(reactor, endpoint, transport_factory, hostname=host)

    # as the reactor/event-loop shuts down, we wish to wait until we've sent
    # out our "Goodbye" message; leave() returns a Deferred that
    # fires when the transport gets to STATE_CLOSED
    def cleanup():
        if hasattr(proto, '_session') and proto._session is not None:
            if proto._session._session_id:
                return proto._session.leave()
    reactor.addSystemEventTrigger('before', 'shutdown', cleanup)

    returnValue(proto)


# this replaces ApplicationRunner, and is the preferred API. Or, call
# Connection.open() yourself, use txaio.start_logging() and run your
# own reactor.
def run(connections, log_level='info', loop=None):
    # be nice if user just passes one connection
    if isinstance(connections, Connection):
        connections = [connections]

    # decide on event-loop (FIXME use choosereactor)
    log = txaio.make_logger()
    txaio.start_logging(level=log_level)

    if loop is None:
        from twisted.internet import reactor as loop
    txaio.use_twisted()
    txaio.config.loop = loop

    # open all the connections (in parallel)

    def error(fail):
        log.error("{msg}", msg=txaio.failure_message(fail))
        log.debug("{traceback}", traceback=txaio.failure_format_traceback(fail))

    def success(_):
        log.info('All connections have completed.')
        try:
            loop.stop()
        except ReactorNotRunning:
            pass

    def startup():
        opens = []
        for conn in connections:
            if conn._loop is None:
                conn._loop = loop
            d = conn.open()
            d.addErrback(error)
            opens.append(d)
        done = DeferredList(opens)

        done.addCallback(success)
        # DeferredList never errbacks.
        return done

    loop.callWhenRunning(startup)
    loop.run()


# XXX probably want IConnection to declare API (e.g. so asyncio one
# follows it as well)
# XXX we can probably make this common via txaio as well...


class ApplicationRunner(_ApplicationRunner):
    """
    Provides a high-level API that is (mostly) consistent across
    asyncio and Twisted code. This starts the event-loop/reactor,
    starts logging and provides a place to put all your configuration
    information.

    If you want more control over the reactor and logging, see the
    :class:`Connection` class, a lower-level interface (which is
    itself used by this class).

    If you need even lower-level control than that, see
    :meth:`connect_to` which attempts a single connection to a single
    transport.

    There is a single event this class emits upon which you may
    listen, and that is ``connection`` which is fired whenever a new
    Connection instance is created; this receives a single argument:
    the new instance. You can use this event to add listeners on the
    ``connection.session`` instance, which will be an
    ``ApplicationSession`` (or subclass) instance.
    """

    def run(self, session_factory, start_reactor=True):
        """
        Run an application component.

        :param session_factory: A callable that produces instances of
           :class:`autobahn.asyncio.wamp.ApplicationSession` when
           called with an instance of
           :class:`autobahn.wamp.types.ComponentConfig`. Usually this
           is simply your ``ApplicationSession`` subclass.
        :type make: callable

        :param start_reactor: if True (the default) this method starts
           the Twisted reactor and doesn't return until the reactor
           stops. If there are any problems starting the reactor or
           connect()-ing, we stop the reactor and raise the exception
           back to the caller.

        :returns: None is returned, unless you specify
            ``start_reactor=False`` in which case you get a Deferred
            that will callback() with a Connection instance when a
            connection is first established (WAMP session not yet
            joined at this point).
        """
        loop = self._loop
        if loop is None:
            from twisted.internet import reactor as loop
        txaio.use_twisted()
        txaio.config.loop = loop

        # XXX FIXME should we really start logging automagically? or
        # not... or provide a "start_logging=True" kwarg?

        # XXX I guess the "experts" interface is:
        # Connection(..).open() and then you can start logging however you want...?
        txaio.start_logging(out=sys.stdout, level='info')

        connection = Connection(
            self._transports,
            session_factory,
            realm=self.realm,
            extra=self.extra,
            loop=loop,
        )

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
                    self.log.critical(txaio.failure_message(failure))
            connect_error = ErrorCollector()

            def shutdown(_):
                try:
                    IReactorCore(loop).stop()
                except ReactorAlreadyRunning:
                    pass

            def startup():
                d = connection.open()
                d.addErrback(connect_error)
                d.addBoth(shutdown)
                return d
            IReactorCore(loop).callWhenRunning(startup)

            # now enter the Twisted reactor loop
            IReactorCore(loop).run()

            # if we exited due to a connection error, raise that to the
            # caller
            if connect_error.exception:
                raise connect_error.exception

        else:
            # let the caller handle any errors
            d = connection.open()
            # we return a Connection instance ("_" will be IProtocol)
            d.addCallback(lambda _: connection)
            return d

    def _create_session(self, cfg):
        """
        Internal helper
        """
        self.session = self._session_factory(cfg)
        return self.session


class _ApplicationSession(ApplicationSession):
    """
    WAMP application session class used internally with
    :class:`autobahn.twisted.app.Application`.
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

    log = txaio.make_logger()

    def __init__(self, prefix=None):
        """
        :param prefix: The application URI prefix to use for
           procedures and topics, e.g. ``"com.example.myapp"``.
        :type prefix: unicode
        """
        self._prefix = prefix

        #: procedures to be registered once the app session has joined
        #: the router/realm
        self._procs = []

        #: event handler to be subscribed once the app session has
        #: joined the router/realm
        self._handlers = []

        #: app lifecycle signal handlers
        self._signals = {}

        #: once an app session is connected, this will be that instance
        # XXX maybe list intead? so we can start many?
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
            start_reactor=True):
        """
        Run the application.

        :param url: The URL of the WAMP router to connect to.
        :type url: unicode

        :param realm: The realm on the WAMP router to join.
        :type realm: unicode
        """
        runner = ApplicationRunner(url, realm)
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
                self.log.info("Warning: exception in signal handler swallowed", e)


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
