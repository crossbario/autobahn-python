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

from autobahn.websocket.protocol import parseWsUrl


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
    # XXX use if's and real exception instead of assert()s
    for key in transport.keys():
        assert key in ['type', 'url', 'endpoint']

    kind = transport.get('type', 'websocket')
    assert kind in ['websocket', 'rawsocket']

    if kind == 'websocket':
        assert 'url' in transport
        is_secure, host, port, resource, path, params = parseWsUrl(transport['url'])
        if not is_secure and 'tls' in transport:
            raise RuntimeError(
                '"tls" key conflicts with the "ws:" prefix of the url'
                ' argument. Did you mean to use "wss:"?'
            )

    if 'endpoint' in transport:
        return check_endpoint(transport['endpoint'], listen=listen)
    else:
        if kind != 'websocket':
            raise RuntimeError("Must provide 'endpoint' configuration "
                               "for '{}'".format(transport['type']))
        return True


def check_retry(cfg):
    """
    Checks that the given configuration is a valid retry-logic configuration.

    :param cfg: A dict containing keys:

    - ``max_retries``: maximum attempts before giving up
    """
    # XXX FIXME
    return True


# XXX could also allow "endpoint" to be a string, and if so
# treat it as a Twisted endpoint-string?
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

    :returns: True if this is a valid endpoint, or an exception otherwise
    """

    valid_keys = [
        'type', 'port', 'version', 'interface', 'backlog', 'shared',
        'tls', 'path', 'host',
    ]
    for key in endpoint.keys():
        assert key in valid_keys, "Invalid key '{}'".format(key)

    kind = endpoint.get('type', 'tcp')
    assert kind in ['tcp', 'unix']
    if kind == 'tcp':
        assert 'path' not in endpoint
        if not listen:
            assert 'host' in endpoint
            assert 'interface' not in endpoint
        version = endpoint.get('version', 4)
        assert version in [4, 6]
    else:
        for x in ['host', 'port', 'interface', 'tls', 'shared', 'version']:
            assert x not in endpoint
        assert 'path' in endpoint
        if 'tls' in endpoint:
            raise RuntimeError("No TLS in Unix sockets")

    timeout = float(endpoint.get('timeout', 10))
    assert timeout > 0.0

    if listen:
        assert 'timeout' not in endpoint
    else:
        assert 'backlog' not in endpoint
        assert 'shared' not in endpoint
        assert 'interface' not in endpoint

    return True
