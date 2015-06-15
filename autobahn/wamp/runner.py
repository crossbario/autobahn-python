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

## XXX trying to factor out common ApplicationRunner stuff for
## asyncio/twisted

from types import StringType, ListType
from functools import wraps
import json
import six
import txaio

from autobahn.wamp import transport
from autobahn.wamp.exception import TransportLost

# XXX move to transport?
class Connection(object):
    """
    This represents configuration of a protocol and transport to make
    a WAMP connection to particular endpoints.

     - a WAMP protocol is "websocket" or "rawsocket"
     - the transport is TCP4, TCP6 (with or without TLS) or Unix socket.
     - both ``.protocol`` and ``.transport`` are "native"
       objects. That is, if you're using Twisted ``.protocol`` will be
       an IProtocol whereas it will be a BaseProtocol subclass under
       asyncio

    This class handles the lifecycles of the underlying transport/protocol
    pair, providing notifications of transitions.

    XXX make docs generic between tx/asyncio if this is generic

    If :class:`ApplicationRunner <autobahn.twisted.wamp.ApplicationRunner`
    API is too high-level for your use-case, Connection lets you set
    up your own logging, call ``reactor.run()`` yourself,
    etc. ApplicationRunner in fact simply uses Connection internally.

    :ivar protocol: current protocol instance, or ``None``
    :type protocol: tx:`twisted.internet.interfaces.IProtocol` or ``BaseProtocol`` subclass

    :ivar session: current ApplicationSession instance, or ``None``
    :type session: class:`autobahn.wamp.protocol.ApplicationSession` subclass

    :ivar connect_count: how many times we've successfully connected
        ("connected" at the transport level, *not* WAMP session "onJoin"
        level)
    """

    # XXX just make these strings for easier debugging? object() makes
    # it clear you have to use Connection.ERROR etc though...

    # possible events that we emit; if adding one, add to
    # _event_listeners dict too
    ERROR = object()  #: callback gets Exception instance
    CREATE_SESSION = object()  #: callback gets ApplicationSession instance
    SESSION_LEAVE = object()  #: callback gets ApplicationSession instance
    CONNECTED = object()  #: callback gets IProtocol instance
    CLOSED = object()  #: callback gets reason (string) + details (CloseDetails instance)
                       #: reason is "lost", "closed" or "unreachable"

    def __init__(self, session_factory, transports, realm, extra):
        """
        :param session_factory: callable that takes a ComponentConfig and
            returns a new ApplicationSession subclass

        :param transports: a list of dicts configuring available
            transports. See :meth:`autobahn.wamp.transport.check` for
            valid keys
        :type transports: list of dicts

        :param realm: the realm to join
        :type realm: unicode

        :param extra: an object available as 'self.config.extra' in
            your ApplicationSession subclass. Can be anything, e.g
            dict().
        """

        # public state (part of the API)
        self.protocol = None
        self.session = None
        self.connect_count = 0
        self.attempt_count = 0

        # private state + config
        self._session_factory = session_factory
        self._realm = realm
        self._extra = extra
        self._connecting = None  # a Deferred/Future while connecting

        # our event listeners
        self._event_listeners = {
            self.ERROR: [],
            self.CREATE_SESSION: [],
            self.SESSION_LEAVE: [],
            self.CONNECTED: [],
            self.CLOSED: [],
        }

        # generate a new transport to try
        def transport_gen():
            while True:
                for tr in transports:
                    yield tr
        self._transport_gen = transport_gen()

        # ifdef which connect_to we need
        if txaio.using_twisted:
            from autobahn.twisted.wamp import connect_to
        else:
            from autobahn.asyncio.wamp import connect_to
        self._connect_to = connect_to

    def add_event(self, event_type, cb):
        """
        Add a listener for the given ``event_type``; the callback ``cb``
        takes a single argument, whose value depends on the
        event.

        XXX should CLOSED be an exception and take CloseDetails also?
        but only when "closed" state?! (like AutobahnJS)

        Valid events are:

         - ``ERROR``: called with Exception whenever a connect() attempt fails
         - ``CREATE_SESSION``: called with ApplicationSession instance upon session creation
         - ``SESSION_LEAVE``: called with ApplicationSession instance when session leaves
         - ``CONNECTED``: called with IProtocol instance when transport connects
         - ``CLOSED``: called when transport disconnects with "unreachable", "lost", or "closed"
        """
        try:
            self._event_listeners[event_type].append(cb)
        except KeyError:
            raise ValueError("Unknown event-type '{}'".format(event_type))

    def remove_event(self, event_type, cb):
        """
        Stop listening.
        """
        try:
            self._event_listeners[event_type].remove(cb)
        except ValueError:
            msg = "Callback '{}' not found for event '{}'"
            raise ValueError(msg.format(cb, event_type))
        except KeyError:
            msg = "No listeners for event '{}'"
            raise ValueError(msg.format(event_type))

    # XXX actually, just this thing needs custom implementation for asyncio vs. Twisted?


    def open(self, loop):
        """
        Starts connecting (possibly also re-connecting) and returns a
        Deferred/Future that fires (with None) when we first connect.
        """
        # XXX for now, all we look at is the first transport! ...this
        # will get fixed with retry-logic

        if self._connecting is not None:
            raise RuntimeError("Already connecting.")

        transport_config = next(self._transport_gen)
        transport.check(transport_config, listen=False)

        self.attempt_count += 1
        self._connecting = txaio.as_future(
            self._connect_to, loop, transport_config,
            self._create_session, self._realm, self._extra,
        )

        def on_error(fail):
            print("Error connecting to '{}': {}".format(
                json.dumps(transport_config), fail))
            # seems redundant but for retry-logic, we can only
            # Deferred-error on the very first connect_to() attempt
            self._fire_event(self.ERROR, fail)
            return fail

        def on_success(proto):
            self.protocol = proto

            # "listen" for connectionLost

            # XXX this smells ... bad. Perhaps adding something we can
            # listen to on transports, that has the same return value
            # for twisted/asyncio (maybe just "closed" or "lost"?)
            # ... or this whole "shared impl for Connection" approach is flawed?
            # XXX basically: get rid of framework-specific "ifdef"s from here

            if txaio.using_twisted:
                orig = self.protocol.transport.connectionLost
            else:
                orig = self.protocol.connection_lost

            @wraps(orig)
            def wrapper(*args, **kw):
                rtn = orig(*args, **kw)

                if txaio.using_twisted:
                    # first arg is a Failure
                    exc = args[0].value
                    from twisted.internet.error import ConnectionDone
                    if isinstance(exc, ConnectionDone):
                        exc = None
                else:
                    # first arg is the Exception, or None if clean
                    exc = args[0]

                if self.connect_count == 0:
                    self._fire_event(self.CLOSED, "unreachable")
                else:
                    if exc is None:
                        self._fire_event(self.CLOSED, "closed")
                    else:
                        # XXX javascrpt allows this to return
                        # "false" to cancel reconnection
                        self._fire_event(self.CLOSED, "lost")
                self.protocol = None
                return rtn
            if txaio.using_twisted:
                self.protocol.transport.connectionLost = wrapper
            else:
                self.protocol.connection_lost = wrapper

        txaio.add_callbacks(self._connecting, on_success, on_error)
        return self._connecting

    def close(self):
        """
        Nicely close the session and/or transport. Returns a
        Deferred/Future that callbacks (with None) when we've closed
        down. throws RuntimeError if the connection is already closed.
        """

        if self.session is not None:
            return self.session.leave()
        elif self.protocol:
            try:
                if txaio.using_twisted:
                    self.protocol.close()
                else:
                    self.protocol.lost_connection()
                return self.protocol.is_closed
            except TransportLost:
                # mimicing JS API, but...
                # XXX is this really an error? could just ignore it ...
                # or should provide ".is_open()" so you can avoid errors :/
                #raise RuntimeError('Connection already closed.')
                f = txaio.create_future()
                txaio.resolve(f, None)
                return f

    def _fire_event(self, evt, *args, **kw):
        """
        Internal helper. MUST NOT throw Exceptions
        """
        # print("FIRE", self._event_to_name(evt), args)
        for cb in self._event_listeners[evt]:
            try:
                cb(*args, **kw)
            except Exception as e:
                print("While running callback '{}' for '{}': {}".format(
                    cb, self._event_to_name(evt), e))
                import traceback
                traceback.print_exc()

    def _event_to_name(self, evt):
        for (k, v) in self.__class__.__dict__.items():
            if v == evt:
                return k
        return 'unknown'

    def _create_session(self, cfg):
        self.session = self._session_factory(cfg)
        self._fire_event(self.CREATE_SESSION, self.session)
        self.connect_count += 1

        # "listen" for onLeave
        on_leave = self.session.onLeave

        @wraps(self.session.onLeave)
        def wrapper(*args, **kw):
            # callback with the Failure instance
            rtn = on_leave(*args, **kw)
            self._fire_event(self.SESSION_LEAVE, self.session)
            self.session = None  # must come *after* callbacks
            return rtn
        self.session.onLeave = wrapper

        # "listen" for disconnect/leave so we know if we should keep
        # re-trying or not ...
        # this means: disconnect() and we keep reconnecting; leave() and we stop
        leave = self.session.leave
        @wraps(self.session.leave)
        def wrapper(*args, **kw):
            rtn = leave(*args, **kw)
            self._shutting_down = True
            return rtn
        self.session.leave = wrapper

        return self.session

    def __str__(self):
        return "<Connection session={} protocol={} attempts={} connected={}>".format(
            self.session.__class__.__name__, self.protocol.__class__.__name__,
            self.attempt_count, self.connect_count)


class _ApplicationRunner(object):
    """
    Internal use.

    This is a common base-class between asyncio and Twisted; you
    should use one of the framework-specific subclasses:

    - autobahn.twisted.wamp.ApplicationRunner
    - autobahn.twisted.asyncio.ApplicationRunner
    """

    # XXX FIXME debug, debug_wamp etc. If we want to keep something
    # similar, put it in the transport config?
    def __init__(self, url_or_transports, realm, extra=None,
                 debug=False, debug_wamp=False, debug_app=False):
        """
        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode

        :param url_or_transports:
            an iterable of dicts, each one configuring WAMP transport
            options, possibly including an Endpoint to connect
            to. WebSocket connections can implicitly derive a TCP4
            endpoint from the URL (and 'websocket' is the default
            type), so a websocket connection can be simply:
            ``transports={"url": "ws://demo.crossbar.io/ws"}``.

            If you pass a single string instead of an iterable, it is
            treated as a WebSocket URL and a single TCP4 transport is
            automatically created.
        :type url_or_transports: iterable (of dicts)

        :param extra: Optional extra configuration to forward to the
            application component.
        :type extra: any object

        :param debug: Turn on low-level debugging.
        :type debug: bool

        :param debug_wamp: Turn on WAMP-level debugging.
        :type debug_wamp: bool

        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool
        """

        self.realm = realm
        self.extra = extra or dict()
        self.debug = debug
        self.debug_wamp = debug_wamp
        self.debug_app = debug_app
        self.make = None
        self._protocol = None
        self._session = None
        if type(url_or_transports) in [StringType, six.text_type]:
            # XXX emit deprecation-warning? is it really deprecated?
            _, host, port, _, _, _ = parseWsUrl(url_or_transports)
            self.transports = [{
                "type": "websocket",
                "url": unicode(url_or_transports),
                "endpoint": {
                    "type": "tcp",
                    "host": host,
                    "port": port,
                }
            }]
        else:
            # XXX shall we also handle "passing a single dict" instead of 1-entry list?
            self.transports = url_or_transports

        # validate the transports we have ... but not if they're an
        # iterable. this gives feedback right away for invalid
        # transports if you passed a list, but lets you pass a
        # generator etc. instead if you want
        if type(self.transports) is ListType:
            for cfg in self.transports:
                transport.check(cfg, listen=False)

    def run(self, session_factory, **kw):
        raise RuntimeError("Subclass should override .run()")

