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
from autobahn.websocket.util import parse_url
from autobahn.wamp.types import ComponentConfig

__all__ = ('Connection')


def check_endpoint(endpoint, check_native_endpoint=None):
    """
    Check a WAMP connecting endpoint configuration.
    """
    if type(endpoint) != dict:
        check_native_endpoint(endpoint)
    else:
        if 'type' not in endpoint:
            raise RuntimeError('missing type in endpoint')
        if endpoint['type'] not in ['tcp', 'unix']:
            raise RuntimeError('invalid type "{}" in endpoint'.format(endpoint['type']))

        if endpoint['type'] == 'tcp':
            pass
        elif endpoint['type'] == 'unix':
            pass
        else:
            assert(False), 'should not arrive here'


def check_transport(transport, check_native_endpoint=None):
    """
    Check a WAMP connecting transport configuration.
    """
    if type(transport) != dict:
        raise RuntimeError('invalid type {} for transport configuration - must be a dict'.format(type(transport)))

    if 'type' not in transport:
        raise RuntimeError('missing type in transport')

    if transport['type'] not in ['websocket', 'rawsocket']:
        raise RuntimeError('invalid transport type {}'.format(transport['type']))

    if transport['type'] == 'websocket':
        pass
    elif transport['type'] == 'rawsocket':
        pass
    else:
        assert(False), 'should not arrive here'


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


class Component(ObservableMixin):
    """
    A WAMP application component. A component holds configuration for and knows how to create
    transports and sessions.
    """

    session = None
    """
    The factory of the session we will instantiate.
    """

    TYPE_MAIN = 1
    TYPE_SETUP = 2

    def __init__(self, main=None, setup=None, transports=None, config=None):
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
        """
        ObservableMixin.__init__(self)

        if main is None and setup is None:
            raise RuntimeError('either a "main" or "setup" procedure must be provided for a component')

        if main is not None and setup is not None:
            raise RuntimeError('either a "main" or "setup" procedure must be provided for a component (not both)')

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
            is_secure, host, port, resource, path, params = parse_url(url)
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

        # now check and save list of transports
        self._transports = []
        idx = 0
        for transport in transports:
            check_transport(transport)
            self._transports.append(Transport(idx, transport))
            idx += 1

        self._realm = u'realm1'
        self._extra = None

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
            endpoint_type=transport_config['endpoint']['type'],
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

                if self._entry_type == Component.TYPE_MAIN:

                    def on_join(session, details):
                        self.log.debug("session on_join: {details}", details=details)
                        d = txaio.as_future(self._entry, reactor, session)

                        def main_success(_):
                            self.log.debug("main_success")
                            txaio.resolve(done, None)

                        def main_error(err):
                            self.log.debug("main_error: {err}", err=err)
                            txaio.reject(done, err)

                        txaio.add_callbacks(d, main_success, main_error)

                    session.on('join', on_join)

                elif self._entry_type == Component.TYPE_SETUP:

                    def on_join(session, details):
                        self.log.debug("session on_join: {details}", details=details)
                        d = txaio.as_future(self._entry, reactor, session)

                        def setup_success(_):
                            self.log.debug("setup_success")

                        def setup_error(err):
                            self.log.debug("setup_error: {err}", err=err)

                        txaio.add_callbacks(d, setup_success, setup_error)

                    session.on('join', on_join)

                else:
                    assert(False), 'logic error'

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
                        txaio.resolve(done, None)
                    else:
                        txaio.reject(done, RuntimeError('transport closed uncleanly'))

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
