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

try:
    _TLS = True
    from twisted.internet.endpoints import SSL4ClientEndpoint
    from twisted.internet.ssl import optionsForClientTLS, CertificateOptions
    from twisted.internet.interfaces import IOpenSSLClientConnectionCreator
except ImportError:
    _TLS = False

import txaio

from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.twisted.rawsocket import WampRawSocketClientFactory

from autobahn.wamp import connection

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession


__all__ = ('Connection')


def _create_transport_factory(reactor, transport_config, session_factory):
    """
    Create a WAMP-over-XXX transport factory.
    """
    if transport_config['type'] == 'websocket':
        return WampWebSocketClientFactory(session_factory, url=transport_config['url'])
    elif transport_config['type'] == 'rawsocket':
        return WampRawSocketClientFactory(session_factory)
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


class Connection(connection.Connection):
    """
    A connection establishes a transport and attached a session
    to a realm using the transport for communication.

    The transports a connection tries to use can be configured,
    as well as the auto-reconnect strategy.
    """

    log = txaio.make_logger()

    session = ApplicationSession
    """
    The factory of the session we will instantiate.
    """

    def __init__(self, transports=u'ws://127.0.0.1:8080/ws', realm=u'realm1', extra=None):
        connection.Connection.__init__(self, None, transports, realm, extra)

    def _connect_transport(self, reactor, transport_config, session_factory):
        """
        Create and connect a WAMP-over-XXX transport.
        """
        transport_factory = _create_transport_factory(reactor, transport_config, session_factory)
        transport_endpoint = _create_transport_endpoint(reactor, transport_config['endpoint'])
        return transport_endpoint.connect(transport_factory)

    @inlineCallbacks
    def start(self, reactor=None, main=None):
        if reactor is None:
            from twisted.internet import reactor

        txaio.use_twisted()
        txaio.config.loop = reactor

        txaio.start_logging(level='debug')

        if main:
            main(reactor, self)

        transport_gen = itertools.cycle(self._transports)

        reconnect = True

        while reconnect:
            transport_config = next(transport_gen)
            try:
                yield self._connect_once(reactor, transport_config)
            except Exception as e:
                print(e)
                yield sleep(2)
            else:
                reconnect = False
