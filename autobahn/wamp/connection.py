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

import random
import six

import txaio

from autobahn.util import ObservableMixin
from autobahn.websocket.protocol import parseWsUrl
from autobahn.wamp.types import ComponentConfig

__all__ = ('Connection')


def check_endpoint(endpoint, check_native_endpoint=None):
    """
    :param listen: True if this transport will be used for listening

    :param endpoint:

        A dict defining a network endpoint, consisting of the following keys:

        - type: "tcp" or "unix" (default: tcp)
        - port: (mandatory for TCP) any valid port number
        - version: "4" or "6" (default: 4)
        - host: the host to connect to (or IP address)
        - timeout: (optional) connection timeout in seconds (default: 10)
        - tls: (optional; TCP only) dict of TLS options

        If using Twisted, an "endpoint" can be any object providing
        IStreamClientEndpoint *or* a string that ``clientFromString``
        successfully parses.

    :returns: True if this is a valid endpoint, or an exception otherwise
    """

    if type(endpoint) != dict:
        # if the endpoint isn't a dict, it *must* be a valid "native"
        # object
        if check_native_endpoint is None:
            raise Exception("'endpoint' configuration must be a dict")
        return check_native_endpoint(endpoint)

    # we *do* have a dict here, but we still want to call the native
    # checker if it's available -- for example, if TLS is configured
    # but we have an older Twisted, this fails.
    if check_native_endpoint is not None:
        check_native_endpoint(endpoint)

    valid_keys = ['type', 'port', 'version', 'tls', 'path', 'host', 'timeout']
    for key in endpoint.keys():
        if key not in valid_keys:
            raise Exception("Invalid endpoint key '{0}'".format(key))

    kind = endpoint.get('type', 'tcp')
    if kind not in ['tcp', 'unix']:
        raise Exception("Unknown endpoint kind '{0}'".format(kind))

    if kind == 'tcp':
        if 'path' in endpoint:
            raise Exception("'tcp' endpoints do not accept 'path'")
        if 'host' not in endpoint:
            raise Exception("Client endpoints require 'host'")
        version = endpoint.get('version', 4)
        if version not in [4, 6]:
            raise Exception("Only TCP versions 4 or 6 accepted")

        # 'tls' values are checked by the native checkers
        if 'tls' in endpoint:
            assert check_native_endpoint is not None
    else:
        for x in ['host', 'port', 'tls', 'shared', 'version']:
            if x in endpoint:
                raise Exception("'{0}' not accepted for unix endpoint".format(x))

        if 'path' not in endpoint:
            raise Exception("unix endpoints require 'path'")

    timeout = float(endpoint.get('timeout', 10))
    if timeout <= 0.0:
        raise Exception("Invalid timeout '{0}'".format(timeout))

    return True


def check_transport(transport, check_native_endpoint=None):
    """
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
        return check_endpoint(
            transport['endpoint'],
            check_native_endpoint=check_native_endpoint,
        )
    else:
        if kind != 'websocket':
            raise RuntimeError("Must provide 'endpoint' configuration "
                               "for '{0}'".format(transport['type']))
        return True


class Transport(object):
    """
    Thin-wrapper for WAMP transports used by a Connection.
    """

    def __init__(self, idx, config, max_retries=15, max_retry_delay=300,
                 initial_retry_delay=1.5, retry_delay_growth=1.5,
                 retry_delay_jitter=0.1):
        """

        :param config: The transport configuration.
        :type config: dict
        """
        self.idx = idx
        self.config = config

        self.max_retries = max_retries
        self.max_retry_delay = max_retry_delay
        self.initial_retry_delay = initial_retry_delay
        self.retry_delay_growth = retry_delay_growth
        self.retry_delay_jitter = retry_delay_jitter

        self.reset()

    def reset(self):
        self.connect_attempts = 0
        self.connect_sucesses = 0
        self.connect_failures = 0
        self.retry_delay = self.initial_retry_delay

    def can_reconnect(self):
        return self.connect_attempts < self.max_retries

    def next_delay(self):
        if self.connect_attempts == 0:
            # if we never tried before, try immediately
            return 0
        elif self.connect_attempts >= self.max_retries:
            raise RuntimeError('max reconnects reached')
        else:
            self.retry_delay = self.retry_delay * self.retry_delay_growth
            self.retry_delay = random.normalvariate(self.retry_delay, self.retry_delay * self.retry_delay_jitter)
            if self.retry_delay > self.max_retry_delay:
                self.retry_delay = self.max_retry_delay
            return self.retry_delay


class Connection(ObservableMixin):

    session = None
    """
    The factory of the session we will instantiate.
    """

    def __init__(self, main=None, transports=u'ws://127.0.0.1:8080/ws', realm=u'default', extra=None):
        ObservableMixin.__init__(self)

        if main is not None and not callable(main):
            raise RuntimeError('"main" must be a callable if given')

        if type(realm) != six.text_type:
            raise RuntimeError('invalid type {} for "realm" - must be Unicode'.format(type(realm)))

        # backward compatibility / convenience: allows to provide an URL instead of a
        # list of transports
        if type(transports) == six.text_type:
            url = transports
            is_secure, host, port, resource, path, params = parseWsUrl(url)
            transport = {
                'type': 'websocket',
                'url': url,
                'endpoint': {
                    'type': 'tcp',
                    'host': host,
                    'port': port
                }
            }
            if is_secure:
                # FIXME
                transport['endpoint']['tls'] = {}
            transports = [transport]

        self._transports = []
        idx = 0
        for transport in transports:
            check_transport(transport)
            self._transports.append(Transport(idx, transport))
            idx += 1

        self._main = main
        self._realm = realm
        self._extra = extra

    def _can_reconnect(self):
        # check if any of our transport has any reconnect attempt left
        for transport in self._transports:
            if transport.can_reconnect():
                return True
        return False

    def start(self, reactor):
        raise RuntimeError('not implemented')

    def _connect_once(self, reactor, transport_config):

        self.log.info(
            'connecting once using transport type "{transport_type}" '
            'over endpoint type "{endpoint_type}"',
            transport_type=transport_config['type'],
            endpoint_type=transport_config['endpoint']['type']
        )

        done = txaio.create_future()

        # factory for ISession objects
        def create_session():
            cfg = ComponentConfig(self._realm, self._extra)
            try:
                session = self.session(cfg)
            except Exception:
                # couldn't instantiate session calls, which is fatal.
                # let the reconnection logic deal with that
                raise
            else:
                # hook up the listener to the parent so we can bubble
                # up events happning on the session onto the connection
                session._parent = self

                # listen on leave events
                def on_leave(session, details):
                    self.log.debug("session on_leave: {details}", details=details)

                session.on('leave', on_leave)

                # listen on disconnect events
                def on_disconnect(session, was_clean):
                    self.log.debug("session on_disconnect: {was_clean}", was_clean=was_clean)

                    if was_clean:
                        # eg the session has left the realm, and the transport was properly
                        # shut down. successfully finish the connection
                        done.callback(None)
                    else:
                        done.errback(RuntimeError('transport closed uncleanly'))

                session.on('disconnect', on_disconnect)

                # return the fresh session object
                return session

        d = self._connect_transport(reactor, transport_config, create_session)

        def on_connect_sucess(proto):
            # FIXME: leave / cleanup proto when reactor stops?
            pass

        def on_connect_failure(err):
            # failed to establish a connection in the first place
            done.errback(err)

        txaio.add_callbacks(d, on_connect_sucess, on_connect_failure)

        return done
