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

import six
import txaio
from autobahn.websocket.protocol import parseWsUrl

_TX_TLS = False
_SSL = False
if txaio.using_twisted:
    try:
        from twisted.internet.endpoints import clientFromString, serverFromString
        from twisted.internet.interfaces import IStreamClientEndpoint, IStreamServerEndpoint
    except ImportError:
        # we still support Twisted versions that lack endpoint
        # support; this allows the unit-tests to run...Connection
        # depends on endpoints, however, so ...
        pass

    try:
        _TX_TLS = True
        from twisted.internet.ssl import CertificateOptions
        from twisted.internet.interfaces import IOpenSSLClientConnectionCreator
    except ImportError:
        _TX_TLS = False

else:
    try:
        _SSL = True
        import ssl
    except ImportError:
        _SSL = False


# XXX everything in here can (and should) have a unit-test
def check(transport, listen=False):
    """
    :param listen: True if this transport will be used for listening
        (False means a client connection)

    :param transport:
        a dict defining a WAMP transport. A WAMP transport definition
        consists of the following fields:

        - type: "websocket" or "rawsocket" (default: websocket)
        - url: (only if type==websocket) the websocket url, like ws://demo.crossbar.io/ws
        - endpoint: (optional) a dict defining a network endpoint (see :meth:`check_endpoint`)

    :returns: True if this is a valid WAMP transport, or an exception otherwise
    """
    for key in transport.keys():
        if key not in ['type', 'url', 'endpoint']:
            raise Exception("Unknown key '{0}' in transport config".format(key))

    kind = transport.get('type', 'websocket')
    if kind not in ['websocket', 'rawsocket']:
        raise Exception("Unknown transport type '{0}'".format(kind))

    if 'url' in transport:
        assert(type(transport['url']) == six.text_type)

    if kind == 'websocket':
        if 'url' not in transport:
            raise Exception("'url' is required in transport")
        is_secure, host, port, resource, path, params = parseWsUrl(transport['url'])
        if 'endpoint' in transport:
            if not is_secure and 'tls' in transport['endpoint'] and transport['endpoint']['tls']:
                raise RuntimeError(
                    '"tls" key conflicts with the "ws:" prefix of the url'
                    ' argument. Did you mean to use "wss:"?'
                )

    if 'endpoint' in transport:
        return check_endpoint(transport['endpoint'], listen=listen)
    else:
        if kind != 'websocket':
            raise RuntimeError("Must provide 'endpoint' configuration "
                               "for '{0}'".format(transport['type']))
        return True


def check_endpoint(endpoint, listen=False):
    """
    :param listen: True if this transport will be used for listening

    :param endpoint:

        A dict defining a network endpoint, consisting of the following keys:

        - type: "tcp" or "unix" (default: tcp)
        - port: (mandatory for TCP) any valid port number
        - version: "4" or "6" (default: 4)
        - host: (non-listen only) the host to connect to (or IP address)
        - interface: (optional; TCP listen only) explicit interface to listen on (default: any)
        - backlog: (optional; listen only) accept-queue depth (default: 50)
        - timeout: (optional; non-listen only) connection timeout in seconds (default: 10)
        - shared: (optional; TCP listen only) share socket amongst other processes (default: False)
        - tls: (optional; TCP only) dict of TLS options

        If using Twisted, a "endpoint" can be any object providing
        IStreamClientEndpoint *or* a string that ``clientFromString``
        can parse (or the server equivalents if ``listen`` is True).

    :returns: True if this is a valid endpoint, or an exception otherwise
    """

    if txaio.using_twisted:
        if isinstance(endpoint, (str, six.text_type)):
            # I don't belive there's any limit to what exceptions this
            # might throw, as they're pluggable...
            try:
                if listen:
                    serverFromString(endpoint)
                else:
                    clientFromString(endpoint)
                return True
            except Exception:
                return False

        if IStreamServerEndpoint.providedBy(endpoint):
            if not listen:
                raise Exception("IStreamServerEndpoint only for listening endpoints")
            return True

        if IStreamClientEndpoint.providedBy(endpoint):
            if listen:
                raise Exception("IStreamClientEndpoint only for connecting endpoints")
            return True

    valid_keys = [
        'type', 'port', 'version', 'interface', 'backlog', 'shared',
        'tls', 'path', 'host', 'timeout',
    ]
    for key in endpoint.keys():
        if key not in valid_keys:
            raise Exception("Invalid endpoint key '{0}'".format(key))

    kind = endpoint.get('type', 'tcp')
    if kind not in ['tcp', 'unix']:
        raise Exception("Unknown endpoint kind '{0}'".format(kind))

    if kind == 'tcp':
        if 'path' in endpoint:
            raise Exception("'tcp' endpoints do not accept 'path'")
        if not listen:
            if 'host' not in endpoint:
                raise Exception("Client endpoints require 'host'")
            if 'interface' in endpoint:
                raise Exception("Client endpoints do not accept 'interface'")
        version = endpoint.get('version', 4)
        if version not in [4, 6]:
            raise Exception("Only TCP versions 4 or 6 accepted")
        tls = endpoint.get('tls', None)
        if tls is not None:
            if txaio.using_twisted and not _TX_TLS:
                raise Exception("TLS configured, but no Twisted TLS support (is OpenSSL installed?)")

            if tls is True:
                pass
            else:
                acceptable = False
                if txaio.using_twisted:
                    if IOpenSSLClientConnectionCreator.providedBy(tls):
                        acceptable = True
                    elif isinstance(tls, CertificateOptions):
                        acceptable = True
                    else:
                        raise Exception(
                            "TLS configuration must be bool, "
                            "IOpenSSLClientConnectionCreator provider or "
                            "CertificateOptions instance"
                        )
                else:  # using_asyncio
                    acceptable = False
                    if tls in [True, False]:
                        acceptable = True
                    elif isinstance(tls, ssl.SSLContext):
                        acceptable = True
                    if not acceptable:
                        raise Exception("TLS configuration must be a bool or an ssl.SSLContext")
    else:
        for x in ['host', 'port', 'interface', 'tls', 'shared', 'version']:
            if x in endpoint:
                raise Exception("'{0}' not accepted for unix endpoint".format(x))

        if 'path' not in endpoint:
            raise Exception("unix endpoints require 'path'")

    timeout = float(endpoint.get('timeout', 10))
    if timeout <= 0.0:
        raise Exception("Invalid timeout '{0}'".format(timeout))

    if listen:
        if 'timeout' in endpoint:
            raise Exception("'timeout' not accepted for listening endpoints")
    else:
        for key in ['backlog', 'shared', 'interface']:
            if key in endpoint:
                raise Exception("'{0}' not accepted for client endpoints".format(x))

    return True
