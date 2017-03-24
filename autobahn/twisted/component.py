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


from __future__ import absolute_import, print_function

import itertools
from functools import partial

from twisted.internet.defer import inlineCallbacks  # XXX FIXME?
from twisted.python.failure import Failure
from twisted.internet.interfaces import IStreamClientEndpoint
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.error import ReactorNotRunning

try:
    _TLS = True
    from twisted.internet.endpoints import SSL4ClientEndpoint
    from twisted.internet.ssl import optionsForClientTLS, CertificateOptions
    from twisted.internet.interfaces import IOpenSSLClientConnectionCreator
    from OpenSSL import SSL
except ImportError as e:
    _TLS = False
    if 'OpenSSL' not in str(e):
        raise

import txaio

from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.twisted.rawsocket import WampRawSocketClientFactory

from autobahn.wamp import component, types

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import Session
from autobahn.wamp.exception import ApplicationError


__all__ = ('Component')


def _is_ssl_error(e):
    """
    Internal helper.

    This is so we can just return False if we didn't import any
    TLS/SSL libraries. Otherwise, returns True if this is an
    OpenSSL.SSL.Error
    """
    if _TLS:
        return isinstance(e, SSL.Error)
    return False


def _unique_list(seq):
    """
    Return a list with unique elements from sequence, preserving order.
    """
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def _create_transport_serializer(serializer_id):
    if serializer_id in [u'msgpack', u'mgspack.batched']:
        # try MsgPack WAMP serializer
        try:
            from autobahn.wamp.serializer import MsgPackSerializer
        except ImportError:
            pass
        else:
            if serializer_id == u'mgspack.batched':
                return MsgPackSerializer(batched=True)
            else:
                return MsgPackSerializer()

    if serializer_id in [u'json', u'json.batched']:
        # try JSON WAMP serializer
        try:
            from autobahn.wamp.serializer import JsonSerializer
        except ImportError:
            pass
        else:
            if serializer_id == u'json.batched':
                return JsonSerializer(batched=True)
            else:
                return JsonSerializer()

    raise RuntimeError('could not create serializer for "{}"'.format(serializer_id))


def _create_transport_serializers(transport):
    """
    Create a list of serializers to use with a WAMP protocol factory.
    """
    serializers = []
    for serializer_id in transport.serializers:
        if serializer_id == u'msgpack':
            # try MsgPack WAMP serializer
            try:
                from autobahn.wamp.serializer import MsgPackSerializer
            except ImportError:
                pass
            else:
                serializers.append(MsgPackSerializer(batched=True))
                serializers.append(MsgPackSerializer())

        elif serializer_id == u'json':
            # try JSON WAMP serializer
            try:
                from autobahn.wamp.serializer import JsonSerializer
            except ImportError:
                pass
            else:
                serializers.append(JsonSerializer(batched=True))
                serializers.append(JsonSerializer())

        else:
            raise RuntimeError(
                "Unknown serializer '{}'".format(serializer_id)
            )

    return serializers


def _create_transport_factory(reactor, transport, session_factory):
    """
    Create a WAMP-over-XXX transport factory.
    """
    if transport.type == 'websocket':
        # FIXME: forward WebSocket options
        serializers = _create_transport_serializers(transport)
        return WampWebSocketClientFactory(session_factory, url=transport.url, serializers=serializers)

    elif transport.type == 'rawsocket':
        # FIXME: forward RawSocket options
        serializer = _create_transport_serializer(transport.serializers[0])
        return WampRawSocketClientFactory(session_factory, serializer=serializer)

    else:
        assert(False), 'should not arrive here'


def _create_transport_endpoint(reactor, endpoint_config):
    """
    Create a Twisted client endpoint for a WAMP-over-XXX transport.
    """
    if IStreamClientEndpoint.providedBy(endpoint_config):
        endpoint = IStreamClientEndpoint(endpoint_config)
    else:
        # create a connecting TCP socket
        if endpoint_config['type'] == 'tcp':

            version = int(endpoint_config.get('version', 4))
            host = str(endpoint_config['host'])
            port = int(endpoint_config['port'])
            timeout = int(endpoint_config.get('timeout', 10))  # in seconds
            tls = endpoint_config.get('tls', None)

            # create a TLS enabled connecting TCP socket
            if tls:
                if not _TLS:
                    raise RuntimeError('TLS configured in transport, but TLS support is not installed (eg OpenSSL?)')

                # FIXME: create TLS context from configuration
                if IOpenSSLClientConnectionCreator.providedBy(tls):
                    # eg created from twisted.internet.ssl.optionsForClientTLS()
                    context = IOpenSSLClientConnectionCreator(tls)

                elif isinstance(tls, CertificateOptions):
                    context = tls

                elif tls is True:
                    context = optionsForClientTLS(host)

                else:
                    raise RuntimeError('unknown type {} for "tls" configuration in transport'.format(type(tls)))

                if version == 4:
                    endpoint = SSL4ClientEndpoint(reactor, host, port, context, timeout=timeout)
                elif version == 6:
                    # there is no SSL6ClientEndpoint!
                    raise RuntimeError('TLS on IPv6 not implemented')
                else:
                    assert(False), 'should not arrive here'

            # create a non-TLS connecting TCP socket
            else:
                if version == 4:
                    endpoint = TCP4ClientEndpoint(reactor, host, port, timeout=timeout)
                elif version == 6:
                    try:
                        from twisted.internet.endpoints import TCP6ClientEndpoint
                    except ImportError:
                        raise RuntimeError('IPv6 is not supported (please upgrade Twisted)')
                    endpoint = TCP6ClientEndpoint(reactor, host, port, timeout=timeout)
                else:
                    assert(False), 'should not arrive here'

        # create a connecting Unix domain socket
        elif endpoint_config['type'] == 'unix':
            path = endpoint_config['path']
            timeout = int(endpoint_config.get('timeout', 10))  # in seconds
            endpoint = UNIXClientEndpoint(reactor, path, timeout=timeout)

        else:
            assert(False), 'should not arrive here'

    return endpoint


class Component(component.Component):
    """
    A component establishes a transport and attached a session
    to a realm using the transport for communication.

    The transports a component tries to use can be configured,
    as well as the auto-reconnect strategy.
    """

    log = txaio.make_logger()

    session_factory = Session
    """
    The factory of the session we will instantiate.
    """

    def _check_native_endpoint(self, endpoint):
        if IStreamClientEndpoint.providedBy(endpoint):
            pass
        elif isinstance(endpoint, dict):
            if 'tls' in endpoint:
                tls = endpoint['tls']
                if isinstance(tls, (dict, bool)):
                    pass
                elif IOpenSSLClientConnectionCreator.providedBy(tls):
                    pass
                elif isinstance(tls, CertificateOptions):
                    pass
                else:
                    raise ValueError(
                        "'tls' configuration must be a dict, CertificateOptions or"
                        " IOpenSSLClientConnectionCreator provider"
                    )
        else:
            raise ValueError(
                "'endpoint' configuration must be a dict or IStreamClientEndpoint"
                " provider"
            )

    def _connect_transport(self, reactor, transport, session_factory):
        """
        Create and connect a WAMP-over-XXX transport.
        """
        transport_factory = _create_transport_factory(reactor, transport, session_factory)
        transport_endpoint = _create_transport_endpoint(reactor, transport.endpoint)
        return transport_endpoint.connect(transport_factory)

    # XXX think: is it okay to use inlineCallbacks (in this
    # twisted-only file) even though we're using txaio?
    @inlineCallbacks
    def start(self, reactor=None):
        """
        This starts the Component, which means it will start connecting
        (and re-connecting) to its configured transports. A Component
        runs until it is "done", which means one of:

        - There was a "main" function defined, and it completed successfully;
        - Something called ``.leave()`` on our session, and we left successfully;
        - ``.stop()`` was called, and completed successfully;
        - none of our transports were able to connect successfully (failure);

        :returns: a Deferred that fires (with ``None``) when we are
            "done" or with a Failure if something went wrong.
        """
        if reactor is None:
            self.log.warn("Using default reactor")
            from twisted.internet import reactor

        yield self.fire('start', reactor, self)

        # transports to try again and again ..
        transport_gen = itertools.cycle(self._transports)

        reconnect = True

        self.log.debug('Entering re-connect loop')

        while reconnect:
            # cycle through all transports forever ..
            transport = next(transport_gen)

            # only actually try to connect using the transport,
            # if the transport hasn't reached max. connect count
            if transport.can_reconnect():
                delay = transport.next_delay()
                self.log.debug(
                    'trying transport {transport_idx} using connect delay {transport_delay}',
                    transport_idx=transport.idx,
                    transport_delay=delay,
                )
                yield sleep(delay)
                try:
                    transport.connect_attempts += 1
                    yield self._connect_once(reactor, transport)
                    transport.connect_sucesses += 1
                except Exception as e:
                    transport.connect_failures += 1
                    f = txaio.create_failure()
                    self.log.error(u'component failed: {error}', error=txaio.failure_message(f))
                    self.log.debug(u'{tb}', tb=txaio.failure_format_traceback(f))
                    # If this is a "fatal error" that will never work,
                    # we bail out now
                    if isinstance(e, ApplicationError):
                        if e.error in [u'wamp.error.no_such_realm']:
                            reconnect = False
                            self.log.error(u"Fatal error, not reconnecting")
                            # The thinking here is that we really do
                            # want to 'raise' (and thereby fail the
                            # entire "start" / reconnect loop) because
                            # if the realm isn't valid, we're "never"
                            # going to succeed...
                            raise
                        self.log.error(u"{msg}", msg=e.error_message())
                    elif _is_ssl_error(e):
                        # Quoting pyOpenSSL docs: "Whenever
                        # [SSL.Error] is raised directly, it has a
                        # list of error messages from the OpenSSL
                        # error queue, where each item is a tuple
                        # (lib, function, reason). Here lib, function
                        # and reason are all strings, describing where
                        # and what the problem is. See err(3) for more
                        # information."
                        for (lib, fn, reason) in e.args[0]:
                            self.log.error(u"TLS failure: {reason}", reason=reason)
                        self.log.error(u"Marking this transport as failed")
                        transport.failed()
                    else:
                        f = txaio.create_failure()
                        self.log.error(
                            u'Connection failed: {error}',
                            error=txaio.failure_message(f),
                        )
                        # some types of errors should probably have
                        # stacktraces logged immediately at error
                        # level, e.g. SyntaxError?
                        self.log.debug(u'{tb}', tb=txaio.failure_format_traceback(f))
                else:
                    self.log.debug(u"Not reconnecting")
                    reconnect = False
            else:
                # check if there is any transport left we can use
                # to connect
                if not self._can_reconnect():
                    self.log.info("No remaining transports to try")
                    reconnect = False

    def stop(self):
        return self._session.leave()


# XXX this should move to autobahn/wamp/component.py or somewhere
# generic as this same implementation will work for asyncio
def _run(reactor, components):
    """
    Internal helper. Use "run" method.

    This is called by react() so any errors coming out of this should
    be handled properly. Logging will already be started.
    """
    # let user pass a single component to run, too
    # XXX probably want IComponent? only demand it, here and below?
    if isinstance(components, Component):
        components = [components]

    if type(components) != list:
        raise ValueError(
            '"components" must be a list of Component objects - encountered'
            ' {0}'.format(type(components))
        )

    for c in components:
        if not isinstance(c, Component):
            raise ValueError(
                '"components" must be a list of Component objects - encountered'
                'item of type {0}'.format(type(c))
            )

    # validation complete; proceed with startup
    log = txaio.make_logger()

    def component_success(comp, arg):
        log.debug("Component '{c}' successfully completed: {arg}", c=comp, arg=arg)
        return arg

    def component_failure(comp, f):
        log.error("Component '{c}' error: {msg}", c=comp, msg=txaio.failure_message(f))
        log.debug("Component error: {tb}", tb=txaio.failure_format_traceback(f))
        # double-check: is a component-failure still fatal to the
        # startup process (because we passed consume_exception=False
        # to gather() below?)
        return None

    def component_start(comp):
        # the future from start() errbacks if we fail, or callbacks
        # when the component is considered "done" (so maybe never)
        d = comp.start(reactor)
        txaio.add_callbacks(
            d,
            partial(component_success, comp),
            partial(component_failure, comp),
        )
        return d

    # note that these are started in parallel -- maybe we want to add
    # a "connected" signal to components so we could start them in the
    # order they're given to run() as "a" solution to dependencies.
    dl = []
    for comp in components:
        d = component_start(comp)
        dl.append(d)
    done_d = txaio.gather(dl, consume_exceptions=False)

    def all_done(arg):
        log.debug("All components ended; stopping reactor")
        if isinstance(arg, Failure):
            log.error("Something went wrong: {log_failure}", failure=arg)
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass
    txaio.add_callbacks(done_d, all_done, all_done)
    return done_d


def run(components, log_level='info'):
    """
    High-level API to run a series of components.

    This will only return once all the components have stopped
    (including, possibly, after all re-connections have failed if you
    have re-connections enabled). Under the hood, this calls
    :meth:`twisted.internet.reactor.run` -- if you wish to manage the
    reactor loop yourself, use the
    :meth:`autobahn.twisted.component.Component.start` method to start
    each component yourself.

    :param components: the Component(s) you wish to run
    :type components: Component or list of Components

    :param log_level: a valid log-level (or None to avoid calling start_logging)
    :type log_level: string
    """
    # only for Twisted > 12
    # ...so this isn't in all Twisted versions we test against -- need
    # to do "something else" if we can't import .. :/ (or drop some
    # support)
    from twisted.internet.task import react

    # actually, should we even let people "not start" the logging? I'm
    # not sure that's wise... (double-check: if they already called
    # txaio.start_logging() what happens if we call it again?)
    if log_level is not None:
        txaio.start_logging(level=log_level)
    react(_run, (components, ))
