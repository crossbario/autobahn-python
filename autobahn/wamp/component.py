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
import random
from functools import wraps

import txaio

from autobahn.util import ObservableMixin
from autobahn.websocket.util import parse_url
from autobahn.wamp.types import ComponentConfig
from autobahn.wamp.exception import ApplicationError


__all__ = ('Connection')


def _normalize_endpoint(endpoint, check_native_endpoint=None):
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


def _normalize_transport(transport, check_native_endpoint=None):
    """
    Check a WAMP connecting transport configuration, and add any
    defaults that we can. These are:

    - type: websocket
    - endpoint: if not specified, fill in from URL
    """
    if type(transport) != dict:
        raise RuntimeError('invalid type {} for transport configuration - must be a dict'.format(type(transport)))

    if 'type' not in transport:
        transport['type'] = 'websocket'

    if transport['type'] not in ['websocket', 'rawsocket']:
        raise RuntimeError('invalid transport type {}'.format(transport['type']))

    if transport['type'] == 'websocket':
        if 'url' not in transport:
            raise ValueError("Missing 'url' in transport")
        if 'endpoint' not in transport:
            is_secure, host, port, resource, path, params = parse_url(transport['url'])
            transport['endpoint'] = {
                'type': 'tcp',
                'host': host,
                'port': port,
                'tls': False if not is_secure else dict(hostname=host),
            }
        _normalize_endpoint(transport['endpoint'], check_native_endpoint)
        # XXX can/should we check e.g. serializers here?

    elif transport['type'] == 'rawsocket':
        if 'endpoint' not in transport:
            raise ValueError("Missing 'endpoint' in transport")

    else:
        assert False, 'should not arrive here'


class Transport(object):
    """
    Thin-wrapper for WAMP transports used by a Connection.
    """

    def __init__(self, idx, config, max_retries=15, max_retry_delay=300,
                 initial_retry_delay=1.5, retry_delay_growth=1.5,
                 retry_delay_jitter=0.1):
        """
        :param config: The transport configuration. Should already be
            validated + normalized
        :type config: dict
        """
        self.idx = idx
        self.config = config

        self.max_retries = max_retries
        self.max_retry_delay = max_retry_delay
        self.initial_retry_delay = initial_retry_delay
        self.retry_delay_growth = retry_delay_growth
        self.retry_delay_jitter = retry_delay_jitter

        self._permanent_failure = False

        self.reset()

    def reset(self):
        self.connect_attempts = 0
        self.connect_sucesses = 0
        self.connect_failures = 0
        self.retry_delay = self.initial_retry_delay

    def failed(self):
        """
        Mark this transport as failed, meaning we won't try to connect to
        it any longer (can_reconnect() will always return False afer
        calling this).
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
        :param transports: Transport configurations for creating transports.
        :type transports: None or unicode or list

        :param config: Session configuration.
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

        # now check and save list of transports
        self._transports = []
        idx = 0
        for transport in transports:
            _normalize_transport(transport, self._check_native_endpoint)
            self._transports.append(Transport(idx, transport))
            idx += 1

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
            'connecting to URL "{url}" with "{transport_type}" transport',
            transport_type=transport.config['type'],
            url=transport.config['url'],
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
                            url=transport.config['url'],
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
                            url=transport.config['url'],
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
        d = self._connect_transport(reactor, transport.config, create_session)

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
