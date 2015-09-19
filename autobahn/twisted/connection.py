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

import txaio

from autobahn.wamp import connection
from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import ComponentConfig
from autobahn.twisted.websocket import WampWebSocketClientFactory
from twisted.internet.defer import Deferred

__all__ = ('Connection')


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
        """

        :param main: The
        """
        connection.Connection.__init__(self, None, transports, realm, extra)

    def start(self, reactor=None, main=None):
        """
        Starts the connection. The connection will establish a transport
        and attach a session to a realm using the transport.

        When the transport is lost, a retry strategy is used to start
        reconnect attempts. Retrying ends when maximum configurable limits have
        been reached, or when the connection was ended explicitly.

        This procedure returns a Deferred/Future that will fire when the
        connection is finally done, that is won't reconnect or has ended
        explicitly. When the connection has ended, either successfully or
        with failure, the returned Deferred/Future will fire.

        :returns: obj -- A Deferred or Future.
        """
        if reactor is None:
            from twisted.internet import reactor
            start_reactor = True
        else:
            start_reactor = False

        txaio.use_twisted()
        txaio.config.loop = reactor

        url = u'ws://127.0.0.1:8080/ws'

        isSecure, host, port, resource, path, params = parseWsUrl(url)

        txaio.start_logging(level='debug')

        # factory for use ApplicationSession
        def create():
            cfg = ComponentConfig(self._realm, self._extra)
            try:
                session = self.session(cfg)
            except Exception as e:
                if start_reactor:
                    # the app component could not be created .. fatal
                    self.log.error(str(e))
                    reactor.stop()
                else:
                    # if we didn't start the reactor, it's up to the
                    # caller to deal with errors
                    raise
            else:
                return session

        # create a WAMP-over-WebSocket transport client factory
        transport_factory = WampWebSocketClientFactory(create, url=url, serializers=None)
        from twisted.internet.endpoints import TCP4ClientEndpoint
        client = TCP4ClientEndpoint(reactor, host, port)

        done = Deferred()
        d = client.connect(transport_factory)

        # as the reactor shuts down, we wish to wait until we've sent
        # out our "Goodbye" message; leave() returns a Deferred that
        # fires when the transport gets to STATE_CLOSED
        def cleanup(proto):
            done.callback(None)
            if hasattr(proto, '_session') and proto._session is not None:
                return proto._session.leave()

        # when our proto was created and connected, make sure it's cleaned
        # up properly later on when the reactor shuts down for whatever reason
        def init_proto(proto):
            reactor.addSystemEventTrigger('before', 'shutdown', cleanup, proto)
            return proto

        # if we connect successfully, the arg is a WampWebSocketClientProtocol
        d.addCallback(init_proto)

        return done

        # if the user didn't ask us to start the reactor, then they
        # get to deal with any connect errors themselves.
        if start_reactor:
            # if an error happens in the connect(), we save the underlying
            # exception so that after the event-loop exits we can re-raise
            # it to the caller.

            class ErrorCollector(object):
                exception = None

                def __call__(self, failure):
                    self.exception = failure.value
                    # print(failure.getErrorMessage())
                    reactor.stop()
            connect_error = ErrorCollector()
            d.addErrback(connect_error)

            # now enter the Twisted reactor loop
            reactor.run()

            # if we exited due to a connection error, raise that to the
            # caller
            if connect_error.exception:
                raise connect_error.exception

        else:
            # let the caller handle any errors
            return d
