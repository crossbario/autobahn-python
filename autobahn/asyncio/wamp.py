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
import signal

from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.protocol import parseWsUrl
from autobahn.asyncio.websocket import WampWebSocketClientFactory

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed to asyncio
    # noinspection PyUnresolvedReferences
    import trollius as asyncio

import txaio
txaio.use_asyncio()

from autobahn.asyncio.websocket import WampWebSocketClientFactory
from autobahn.wamp.runner import _ApplicationRunner, Connection


__all__ = (
    'ApplicationSession',
    'ApplicationSessionFactory',
    'ApplicationRunner',
    'Connection',
    'connect_to',
)


class ApplicationSession(protocol.ApplicationSession):
    """
    WAMP application session for asyncio-based applications.
    """


class ApplicationSessionFactory(protocol.ApplicationSessionFactory):
    """
    WAMP application session factory for asyncio-based applications.
    """

    session = ApplicationSession
    """
   The application session class this application session factory will use. Defaults to :class:`autobahn.asyncio.wamp.ApplicationSession`.
   """


def _create_tcp4_stream_transport(loop, cfg, wamp_transport_factory):
    """
    Internal helper.

    Creates a TCP4 (possibly with TLS) stream transport.
    """

    is_secure, host, port, resource, path, params = parseWsUrl(cfg['url'])
    ssl = cfg.get('tls', is_secure)
    return asyncio.async(loop.create_connection(wamp_transport_factory, host, port, ssl=ssl))


def _create_unix_stream_transport(loop, cfg, wamp_transport_factory):
    """
    Internal helper.

    Creates a Unix socket as the stream transport.
    """
    return asyncio.async(loop.create_unix_connection(wamp_transport_factory, cfg['path']))


def _connect_stream(loop, cfg, wamp_transport_factory):
    """
    Internal helper.

    Connects the given wamp_transport_factory to a stream endpoint, as
    determined from the cfg that's passed in (which should be just the
    "endpoint" part). Returns Deferred that fires with IProtocol
    """

    if cfg['type'] == 'unix':
        f = _create_unix_stream_transport(loop, cfg, wamp_transport_factory)

    elif cfg['type'] == 'tcp':
        if cfg.get('version', 4) == 4:
            f = _create_tcp4_stream_transport(loop, cfg, wamp_transport_factory)
        else:
            raise RuntimeError("FIXME: IPv6 asyncio")
    else:
        raise RuntimeError("Unknown type='{}'".format(cfg['type']))

    return f


def _create_wamp_factory(reactor, cfg, session_factory):
    """
    Internal helper.

    This creates the appropriate protocol-factory (that implements
    tx:`IProtocolFactory <twisted.internet.interfaces.IProtocolFactory>`)

    XXX deal with debug/debug_wamp etcetc.
    """

    if cfg['type'] == 'rawsocket':
        raise RuntimeError("No rawsocket/asyncio impl")

    # only other type is websocket
    return WampWebSocketClientFactory(session_factory, url=cfg['url'])


# XXX counter-intuitively (?) this is called via the common Connection
# class in wamp/runner.py when used internally -- but does need a
# custom asyncio/twisted implementation because of the different way
# shutdown works.


@asyncio.coroutine
def connect_to(loop, transport_config, session_factory, realm, extra, on_error=None):
    """
    :param transport_config: dict containing valid client transport
    config (see :mod:`autobahn.wamp.transport`)

    :param session_factory: callable that takes a ComponentConfig and
    returns a new ISession instance (usually simply your
    ApplicationSession subclass)

    :param on_error: a callable that takes an Exception, called if we
    get an error connecting

    :returns: Future that callbacks with a protocol instance after a
    connection has been made (not necessarily a WAMP session joined
    yet, however)
    """

    def create():
        try:
            session = session_factory(ComponentConfig(realm, extra))
            # XXX FIXME session.debug_app = self.debug_app
            return session

        except Exception as e:
            if on_error:
                on_error(e)
            else:
                log.err("Exception while creating session: {0}".format(e))
            raise

    transport_factory = _create_wamp_factory(loop, transport_config, create)
    f0 = _connect_stream(loop, transport_config['endpoint'], transport_factory)

    # mutate the return value of _connect_stream to be just the
    # protocol so that the API of connect_to is the "same" for Twisted
    # and asyncio (although the protocol returned is a native Twisted
    # or asyncio object).
    # both provide protocol.transport to get the transport

    # XXX is there a better idiom for this in asyncio?
    f1 = asyncio.Future()
    def return_proto(result):
        try:
            transport, protocol = result.result()
            transport.connectionLost = protocol.connection_lost
            f1.set_result(protocol)
        except Exception as e:
            f1.set_exception(e)
    f0.add_done_callback(return_proto)
    return f1


class ApplicationRunner(_ApplicationRunner):
    """
    Provides a high-level API that is (mostly) consistent across
    asyncio and Twisted code.

    If you want more control over the reactor and logging, see the
    :class:`autobahn.wamp.runner.Connection` class.

    If you need lower-level control than that, see :meth:`connect_to`
    which attempts a single connection to a single transport.
    """

    def run(self, session_factory):
        """
        Run the application component.

        :param session_factory: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type session_factory: callable
        """

        # set up the event-loop and ensure txaio is using the same one
        loop = asyncio.get_event_loop()
        txaio.use_asyncio()
        txaio.config.loop = loop

        # want to shut down nicely on TERM
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

        self.connection = Connection(
            session_factory,
            self.transports,
            self.realm,
            self.extra,
        )

        def on_error(e):
            if e is not None:
                print("Error:", e)
        self.connection.add_event(Connection.ERROR, on_error)

        # synchronously start the protocol (retry logic to come)
        protocol = loop.run_until_complete(self.connection.open(loop))

        # now enter the asyncio event loop
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            # wait until we send Goodbye if user hit ctrl-c
            # (done outside this except so SIGTERM gets the same handling)
            pass

        # give Goodbye message a chance to go through, if we still
        # have an active session
        if hasattr(protocol, '_session') and protocol._session is not None:
            loop.run_until_complete(protocol._session.leave())
        loop.close()
