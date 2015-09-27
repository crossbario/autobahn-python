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

import itertools

from twisted.internet.defer import inlineCallbacks
from twisted.internet.interfaces import IStreamClientEndpoint
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.task import react

try:
    _TLS = True
    from twisted.internet.endpoints import SSL4ClientEndpoint
    from twisted.internet.ssl import optionsForClientTLS, CertificateOptions
    from twisted.internet.interfaces import IOpenSSLClientComponentCreator
except ImportError:
    _TLS = False

import txaio

from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.twisted.rawsocket import WampRawSocketClientFactory

from autobahn.wamp import component

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession


__all__ = ('Component')


def _unique_list(seq):
    """
    Return a list with unique elements from sequence, preserving order.
    """
    seen = set(seq)
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


def _create_transport_serializers(transport_config):
    """
    Create a list of serializers to use with a WAMP protocol factory.
    """
    if u'serializers' in transport_config:
        serializer_ids = _unique_list(transport_config['serializers'])
    else:
        serializer_ids = [u'msgpack', u'json']

    serializers = []

    for serializer_id in serializer_ids:
        if serializer_id == u'msgpack':
            # try MsgPack WAMP serializer
            try:
                from autobahn.wamp.serializer import MsgPackSerializer
            except ImportError:
                pass
            else:
                serializers.append(MsgPackSerializer(batched=True))
                serializers.append(MsgPackSerializer())

        if serializer_id == u'json':
            # try JSON WAMP serializer
            try:
                from autobahn.wamp.serializer import JsonSerializer
            except ImportError:
                pass
            else:
                serializers.append(JsonSerializer(batched=True))
                serializers.append(JsonSerializer())

    return serializers


def _create_transport_factory(reactor, transport_config, session_factory):
    """
    Create a WAMP-over-XXX transport factory.
    """
    if transport_config['type'] == 'websocket':
        # FIXME: forward WebSocket options
        serializers = _create_transport_serializers(transport_config)
        return WampWebSocketClientFactory(session_factory, url=transport_config['url'], serializers=serializers)

    elif transport_config['type'] == 'rawsocket':
        # FIXME: forward RawSocket options
        serializer = _create_transport_serializer(transport_config.get('serializer', u'json'))
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
                if IOpenSSLClientComponentCreator.providedBy(tls):
                    # eg created from twisted.internet.ssl.optionsForClientTLS()
                    context = IOpenSSLClientComponentCreator(tls)

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

    session = ApplicationSession
    """
    The factory of the session we will instantiate.
    """

    def _connect_transport(self, reactor, transport_config, session_factory):
        """
        Create and connect a WAMP-over-XXX transport.
        """
        transport_factory = _create_transport_factory(reactor, transport_config, session_factory)
        transport_endpoint = _create_transport_endpoint(reactor, transport_config['endpoint'])
        return transport_endpoint.connect(transport_factory)

    @inlineCallbacks
    def start(self, reactor=None):
        if reactor is None:
            from twisted.internet import reactor

        # txaio.use_twisted()
        # txaio.config.loop = reactor

        # txaio.start_logging(level='debug')

        yield self.fire('start', reactor, self)

        # transports to try again and again ..
        transport_gen = itertools.cycle(self._transports)

        reconnect = True

        self.log.info('entering recomponent loop')

        while reconnect:
            # cycle through all transports forever ..
            transport = next(transport_gen)

            # only actually try to connect using the transport,
            # if the transport hasn't reached max. connect count
            if transport.can_reconnect():
                delay = transport.next_delay()
                self.log.debug('trying transport {transport_idx} using connect delay {transport_delay}', transport_idx=transport.idx, transport_delay=delay)
                yield sleep(delay)
                try:
                    transport.connect_attempts += 1
                    yield self._connect_once(reactor, transport.config)
                    transport.connect_sucesses += 1
                except Exception as e:
                    transport.connect_failures += 1
                    self.log.error(u'component failed: {error}', error=e)
                else:
                    reconnect = False
            else:
                # check if there is any transport left we can use
                # to connect
                if not self._can_reconnect():
                    reconnect = False


def _run(reactor, components):
    if isinstance(components, Component):
        components = [components]

    if type(components) != list:
        raise RuntimeError('"components" must be a list of Component objects - encountered {0}'.format(type(components)))

    for c in components:
        if not isinstance(c, Component):
            raise RuntimeError('"components" must be a list of Component objects - encountered item of type {0}'.format(type(c)))

    # all components are started in parallel
    dl = []
    for c in components:
        # a component can be of type MAIN or SETUP
        dl.append(c.start(reactor))

    d = txaio.gather(dl, consume_exceptions=True)

    return d


def run(components):
    react(_run, [components])
