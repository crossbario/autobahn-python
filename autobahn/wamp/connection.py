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

from autobahn.util import ObservableMixin
from autobahn.websocket.protocol import parseWsUrl
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

        for transport in transports:
            check_transport(transport)

        self._main = main
        self._transports = transports
        self._realm = realm
        self._extra = extra

    def start(self, reactor):
        raise RuntimeError('not implemented')

    def _connect_once(self, reactor, transport_config):

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
                # let child listener bubble up event
                session._parent = self

                # listen on leave events
                def on_leave(session, details):
                    print("on_leave: {}".format(details))

                session.on('leave', on_leave)

                # listen on disconnect events
                def on_disconnect(session, was_clean):
                    print("on_disconnect: {}".format(was_clean))
                    if was_clean:
                        done.callback(None)
                    else:
                        done.errback(RuntimeError('transport closed uncleanly'))

                session.on('disconnect', on_disconnect)

                # return the fresh session object
                return session

        d = self._connect_transport(reactor, transport_config, create_session)

        def on_connect_sucess(res):
            print('on_connect_sucess', res)

        def on_connect_failure(err):
            print('on_connect_failure', err)
            done.errback(err)

        txaio.add_callbacks(d, on_connect_sucess, on_connect_failure)

        return done
