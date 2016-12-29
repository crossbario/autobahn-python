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


from __future__ import absolute_import

import six
import random
from functools import wraps

import txaio

from autobahn.util import ObservableMixin
from autobahn.websocket.util import parse_url
from autobahn.wamp.types import ComponentConfig
from autobahn.wamp.exception import ApplicationError


__all__ = ('Connection')


def _validate_endpoint(endpoint, check_native_endpoint=None):
    """
    Check a WAMP connecting endpoint configuration.
    """
    if check_native_endpoint:
        check_native_endpoint(endpoint)
    elif not isinstance(endpoint, dict):
        raise ValueError(
            "'endpoint' must be a dict"
        )

    # note, we're falling through here -- check_native_endpoint can
    # disallow or allow dict-based config as it likes, but if it
    # *does* allow a dict through, we want to check "base options"
    # here so that both Twisted and asyncio don't have to check these
    # things as well.
    if isinstance(endpoint, dict):
        # XXX what about filling in anything missing from the URL? Or
        # is that only for when *nothing* is provided for endpoint?
        if 'type' not in endpoint:
            # could maybe just make tcp the default?
            raise ValueError("'type' required in endpoint configuration")
        if endpoint['type'] not in ['tcp', 'unix']:
            raise ValueError('invalid type "{}" in endpoint'.format(endpoint['type']))

        for k in endpoint.keys():
            if k not in ['type', 'host', 'port', 'path', 'tls']:
                raise ValueError(
                    "Invalid key '{}' in endpoint configuration".format(k)
                )

        if endpoint['type'] == 'tcp':
            for k in ['host', 'port']:
                if k not in endpoint:
                    raise ValueError(
                        "'{}' required in 'tcp' endpoint config".format(k)
                    )
            for k in ['path']:
                if k in endpoint:
                    raise ValueError(
                        "'{}' not valid in 'tcp' endpoint config".format(k)
                    )
        elif endpoint['type'] == 'unix':
            for k in ['path']:
                if k not in endpoint:
                    raise ValueError(
                        "'{}' required for 'tcp' endpoint config".format(k)
                    )
            for k in ['host', 'port', 'tls']:
                if k in endpoint:
                    raise ValueError(
                        "'{}' not valid for in 'tcp' endpoint config".format(k)
                    )
        else:
            assert False, 'should not arrive here'


def _create_transport(index, transport, check_native_endpoint=None):
    """
    Internal helper to insert defaults and create _Transport instances.

    :param transport: a (possibly valid) transport configuration
    :type transport: dict

    :returns: a _Transport instance

    :raises: ValueError on invalid configuration
    """
    if type(transport) != dict:
        raise ValueError('invalid type {} for transport configuration - must be a dict'.format(type(transport)))

    valid_transport_keys = ['type', 'url', 'endpoint', 'serializer', 'serializers']
    for k in transport.keys():
        if k not in valid_transport_keys:
            raise ValueError(
                "'{}' is not a valid configuration item".format(k)
            )

    kind = 'websocket'
    if 'type' in transport:
        if transport['type'] not in ['websocket', 'rawsocket']:
            raise ValueError('Invalid transport type {}'.format(transport['type']))
        kind = transport['type']

    if kind == 'websocket':
        for key in ['url']:
            if key not in transport:
                raise ValueError("Transport requires '{}' key".format(key))
        # endpoint not required; we will deduce from URL if it's not provided
        # XXX not in the branch I rebased; can this go away? (is it redundant??)
        if 'endpoint' not in transport:
            is_secure, host, port, resource, path, params = parse_url(transport['url'])
            endpoint_config = {
                'type': 'tcp',
                'host': host,
                'port': port,
                'tls': False if not is_secure else dict(hostname=host),
            }
        else:
            # note: we're avoiding mutating the incoming "configuration"
            # dict, so this should avoid that too...
            endpoint_config = transport['endpoint']
            _validate_endpoint(endpoint_config, check_native_endpoint)

        if 'serializer' in transport:
            raise ValueError("'serializer' is only for rawsocket; use 'serializers'")
        if 'serializers' in transport:
            if not isinstance(transport['serializers'], (list, tuple)):
                raise ValueError("'serializers' must be a list of strings")
            if not all([
                    isinstance(s, (six.text_type, str))
                    for s in transport['serializers']]):
                raise ValueError("'serializers' must be a list of strings")
            valid_serializers = ('msgpack', 'json')
            for serial in transport['serializers']:
                if serial not in valid_serializers:
                    raise ValueError(
                        "Invalid serializer '{}' (expected one of: {})".format(
                            serial,
                            ', '.join([repr(s) for s in valid_serializers]),
                        )
                    )
        serializer_config = transport.get('serializers', [u'msgpack', u'json'])

    elif kind == 'rawsocket':
        if 'endpoint' not in transport:
            raise ValueError("Missing 'endpoint' in transport")
        endpoint_config = transport['endpoint']
        if 'serializers' in transport:
            raise ValueError("'serializers' is only for websocket; use 'serializer'")
        # always a list; len == 1 for rawsocket
        if 'serializer' in transport:
            if not isinstance(transport['serializer'], (six.text_type, str)):
                raise ValueError("'serializer' must be a string")
            serializer_config = [transport['serializer']]
        else:
            serializer_config = [u'msgpack']

    else:
        assert False, 'should not arrive here'

    kw = {}
    for key in ['max_retries', 'max_retry_delay', 'initial_retry_delay',
                'retry_delay_growth', 'retry_delay_jitter']:
        if key in transport:
            kw[key] = transport[key]

    return _Transport(
        index,
        kind=kind,
        url=transport['url'],
        endpoint=endpoint_config,
        serializers=serializer_config,
        **kw
    )


class _Transport(object):
    """
    Thin-wrapper for WAMP transports used by a Connection.
    """

    def __init__(self, idx, kind, url, endpoint, serializers,
                 max_retries=15,
                 max_retry_delay=300,
                 initial_retry_delay=1.5,
                 retry_delay_growth=1.5,
                 retry_delay_jitter=0.1):
        """
        """
        self.idx = idx

        self.type = kind
        self.url = url
        self.endpoint = endpoint

        self.serializers = serializers
        if self.type == 'rawsocket' and len(serializers) != 1:
            raise ValueError(
                "'rawsocket' transport requires exactly one serializer"
            )

        self.max_retries = max_retries
        self.max_retry_delay = max_retry_delay
        self.initial_retry_delay = initial_retry_delay
        self.retry_delay_growth = retry_delay_growth
        self.retry_delay_jitter = retry_delay_jitter

        # used via can_reconnect() and failed() to record this
        # transport is never going to work
        self._permanent_failure = False

        self.reset()

    def reset(self):
        """
        set connection failure rates and retry-delay to initial values
        """
        self.connect_attempts = 0
        self.connect_sucesses = 0
        self.connect_failures = 0
        self.retry_delay = self.initial_retry_delay

    def failed(self):
        """
        Mark this transport as failed, meaning we won't try to connect to
        it any longer (that is: can_reconnect() will always return
        False afer calling this).
        """
        self._permanent_failure = True

    def can_reconnect(self):
        if self._permanent_failure:
            return False
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

    def describe_endpoint(self):
        """
        returns a human-readable description of the endpoint
        """
        if isinstance(self.endpoint, dict):
            return self.endpoint['type']
        return repr(self.endpoint)


# this could probably implement twisted.application.service.IService
# if we wanted; or via an adapter...which just adds a startService()
# and stopService() [latter can be async]

class Component(ObservableMixin):
    """
    A WAMP application component. A component holds configuration for
    (and knows how to create) transports and sessions.
    """

    session_factory = None
    """
    The factory of the session we will instantiate.
    """

    TYPE_MAIN = 1
    TYPE_SETUP = 2

    def __init__(self, main=None, setup=None, transports=None, config=None, realm=u'public'):
        """

        :param main: A callable that runs user code for the component. The component will be
            started with a "main-like" procedure. When a transport has been connected and
            a session has been established and joined a realm, the user code will be run until it finishes
            which signals that the component has run to completion.
        :type main: callable
        :param setup: A callable that runs user code for the component. The component will be
            started with a "setup-like" procedure. When a transport has been connected and
            a session has been established and joined a realm, the user code will be run until it finishes
            which signals that the component is now "ready". The component will continue to run until
            it explicitly closes the session or the underlying transport closes.
        :type setup: callable

        :param transports: Transport configurations for creating
            transports. Each transport can be a WAMP URL, or a dict
            containing the following configuration keys:

                - ``type`` (optional): ``websocket`` (default) or ``rawsocket``
                - ``url``: the WAMP URL
                - ``endpoint`` (optional, derived from URL if not provided):
                    - ``type``: "tcp" or "unix"
                    - ``host``, ``port``: only for TCP
                    - ``path``: only for unix
                    - ``timeout``: in seconds
                    - ``tls``: ``True`` or (under Twisted) an
                      ``twisted.internet.ssl.IOpenSSLClientComponentCreator``
                      instance (such as returned from
                      ``twisted.internet.ssl.optionsForClientTLS``) or
                      ``CertificateOptions`` instance.

        :type transports: None or unicode or list of dicts

        :param config: Session configuration (currently unused?)
        :type config: None or dict

        :param realm: the realm to join
        :type realm: unicode
        """
        self.set_valid_events(
            [
                'start',        # fired by base class
                'connect',      # fired by ApplicationSession
                'join',         # fired by ApplicationSession
                'ready',        # fired by ApplicationSession
                'leave',        # fired by ApplicationSession
                'disconnect',   # fired by ApplicationSession
            ]
        )

        if main is not None and not callable(main):
            raise RuntimeError('"main" must be a callable if given')

        if setup is not None and not callable(setup):
            raise RuntimeError('"setup" must be a callable if given')

        if setup:
            self._entry = setup
            self._entry_type = Component.TYPE_SETUP
        elif main:
            self._entry = main
            self._entry_type = Component.TYPE_MAIN
        else:
            assert(False), 'logic error'

        # use WAMP-over-WebSocket to localhost when no transport is specified at all
        if transports is None:
            transports = u'ws://127.0.0.1:8080/ws'

        # allows to provide an URL instead of a list of transports
        if type(transports) == six.text_type:
            url = transports
            # 'endpoint' will get filled in by parsing the 'url'
            transport = {
                'type': 'websocket',
                'url': url,
            }
            transports = [transport]

        # allows a single transport instead of a list (convenience)
        elif isinstance(transports, dict):
            transports = [transports]

        # XXX do we want to be able to provide an infinite iterable of
        # transports here? e.g. a generator that makes new transport
        # to try?

        # now check and save list of transports
        self._transports = []
        for idx, transport in enumerate(transports):
            self._transports.append(
                _create_transport(idx, transport, self._check_native_endpoint)
            )

        self._realm = realm
        self._extra = None  # XXX FIXME

    def _can_reconnect(self):
        # check if any of our transport has any reconnect attempt left
        for transport in self._transports:
            if transport.can_reconnect():
                return True
        return False

    def start(self, reactor):
        raise RuntimeError('not implemented')

    def _connect_once(self, reactor, transport):
        self.log.info(
            'connecting once using transport type "{transport_type}" '
            'over endpoint "{endpoint_desc}"',
            transport_type=transport.type,
            endpoint_desc=transport.describe_endpoint(),
        )

        done = txaio.create_future()

        # factory for ISession objects
        def create_session():
            cfg = ComponentConfig(self._realm, self._extra)
            try:
                session = self.session_factory(cfg)
            except Exception as e:
                # couldn't instantiate session calls, which is fatal.
                # let the reconnection logic deal with that
                f = txaio.create_failure(e)
                txaio.reject(done, f)
                raise
            else:
                # hook up the listener to the parent so we can bubble
                # up events happning on the session onto the
                # connection. This lets you do component.on('join',
                # cb) which will work just as if you called
                # session.on('join', cb) for every session created.
                session._parent = self

                # the only difference bewteen MAIN and SETUP-type
                # entry-points is that we want to shut down the
                # component when a MAIN-type entrypoint's Deferred is
                # done.
                if self._entry_type == Component.TYPE_MAIN:

                    def on_join(session, details):
                        self.log.debug("session on_join: {details}", details=details)
                        transport.connect_sucesses += 1
                        self.log.info(
                            'Successfully connected to transport #{transport_idx}: url={url}',
                            transport_idx=transport.idx,
                            url=transport.url,
                        )
                        d = txaio.as_future(self._entry, reactor, session)

                        def main_success(_):
                            self.log.debug("main_success")
                            session.leave()

                        def main_error(err):
                            self.log.debug("main_error: {err}", err=err)
                            txaio.reject(done, err)
                            # I guess .leave() here too...?

                        txaio.add_callbacks(d, main_success, main_error)

                    session.on('join', on_join)

                elif self._entry_type == Component.TYPE_SETUP:

                    def on_join(session, details):
                        self.log.debug("session on_join: {details}", details=details)
                        self.log.info(
                            'Successfully connected to transport #{transport_idx}: url={url}',
                            transport_idx=transport.idx,
                            url=transport.url,
                        )
                        d = txaio.as_future(self._entry, reactor, session)

                        def setup_success(_):
                            self.log.debug("setup_success")

                        def setup_error(err):
                            self.log.debug("setup_error: {err}", err=err)
                            txaio.reject(done, err)

                        txaio.add_callbacks(d, setup_success, setup_error)

                    session.on('join', on_join)

                else:
                    assert(False), 'logic error'

                # listen on leave events
                def on_leave(session, details):
                    self.log.debug("session on_leave: {details}", details=details)
                    # this could be a "leave" that's expected e.g. our
                    # main() exited, or it could be an error
                    if not txaio.is_called(done):
                        if details.reason.startswith('wamp.error.'):
                            txaio.reject(done, ApplicationError(details.reason, details.message))
                        else:
                            txaio.resolve(done, None)
                session.on('leave', on_leave)

                # listen on disconnect events
                def on_disconnect(session, was_clean):
                    self.log.debug("session on_disconnect: {was_clean}", was_clean=was_clean)

                    if was_clean:
                        # eg the session has left the realm, and the transport was properly
                        # shut down. successfully finish the connection
                        txaio.resolve(done, None)
                    else:
                        txaio.reject(done, RuntimeError('transport closed uncleanly'))

                session.on('disconnect', on_disconnect)

                # return the fresh session object
                return session

        transport.connect_attempts += 1
        d = self._connect_transport(reactor, transport, create_session)

        def on_connect_sucess(proto):
            # if e.g. an SSL handshake fails, we will have
            # successfully connected (here) but need to listen for the
            # "connectionLost" from the underlying protocol in case of
            # handshake failure .. so we wrap it. Also, we don't
            # increment transport.success_count here.
            orig = proto.connectionLost

            @wraps(orig)
            def lost(fail):
                rtn = orig(fail)
                if not txaio.is_called(done):
                    txaio.reject(done, fail)
                return rtn
            proto.connectionLost = lost

        def on_connect_failure(err):
            transport.connect_failures += 1
            # failed to establish a connection in the first place
            done.errback(err)

        txaio.add_callbacks(d, on_connect_sucess, on_connect_failure)

        return done
