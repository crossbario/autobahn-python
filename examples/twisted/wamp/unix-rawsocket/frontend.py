from __future__ import print_function

import random

from twisted.internet.defer import inlineCallbacks, DeferredList, Deferred
from twisted.internet.task import react

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner, Connection, connect_to
from autobahn.twisted.util import sleep


class ClientSession(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        print("Joined", details)
        sub = yield self.subscribe(self.subscription, "test.sub")
        print("subscribed", sub)
        print("disconnecting in 6 seconds")
        yield sleep(6)
        # if you disconnect() then the reconnect logic still keeps
        # trying; if you leave() then it stops trying
        if False:
            print("disconnect()-ing")
            self.disconnect()
        else:
            print("leave()-ing")
            self.leave()

    def subscription(self, *args, **kw):
        print("sub:", args, kw)


@inlineCallbacks
def main(reactor):
    # we set up a transport that will definitely fail to demonstrate
    # re-connection as well. note that "transports" can be an iterable

    bad_transport = {
        "type": "rawsocket",
        "endpoint": {
            "type": "unix",
            "path": "/tmp/cb-raw-foo",
        }
    }

    rawsocket_unix_transport = {
        "type": "rawsocket",
        "endpoint": {
            "type": "unix",
            "path": "/tmp/cb-raw",
        }
    }

    websocket_tcp_transport = {
        "type": "websocket",
        "url": "ws://127.0.0.1/ws",
        "endpoint": {
            "type": "tcp",
            "host": "127.0.0.1",
            "port": 8081,
        }
    }

    transports = [bad_transport, rawsocket_unix_transport, websocket_tcp_transport, {"just": "completely bogus"}]
    def random_transports():
        while True:
            t = random.choice(transports)
            # print("Returning transport:", t)
            yield t

    if False:
        # use generator/iterable as infinite transport list
        runner = ApplicationRunner(random_transports(), u"realm1")

        # single, good unix transport
        #runner = ApplicationRunner([rawsocket_unix_transport], u"realm1")

        # single, good tcp+websocket transport
        #runner = ApplicationRunner([websocket_tcp_transport], u"realm1")

        # single, bad transport (will never succeed)
        #runner = ApplicationRunner([bad_transport], u"realm1")

        # "advanced" usage, passing "start_reactor=False" so we get access to the connection object
        connection = yield runner.run(ClientSession, start_reactor=False)

    elif True:
        # ...OR should just eliminate ^ start_reactor= and "make" you use
        # the Connection API directly if you want a Connection instance? like this:
        connection = Connection(ClientSession, random_transports(), u"realm1", extra=None)
        yield connection.open(reactor)

    else:
        # lowest-level API, connecting a single transport, yielding an IProtocol
        # XXX consider making this one private for now? i.e. "_connect_to"
        connection = None
        proto = yield connect_to(reactor, rawsocket_unix_transport, ClientSession, u"realm1", None)
        print("Protocol", proto)
        yield sleep(10)
        print("done.")

    if connection is not None:
        print("Connection!", connection)
        connection.add_event(Connection.CREATE_SESSION, lambda s: print("new session:", s))
        connection.add_event(Connection.SESSION_LEAVE, lambda s: print("session gone:", s))
        connection.add_event(Connection.CONNECTED, lambda p: print("protocol connected:", p))
        connection.add_event(Connection.ERROR, lambda e: print("connection error:", e))

        stopping = []
        def shutdown(reason):
            print("shutdown because '{}'".format(reason))
            stopping.append(False)
        connection.add_event(Connection.CLOSED, shutdown)

        while not stopping:
            yield sleep(1)
            print("connection:", connection)
            if connection.session:
                # we're doing this so there's "some" traffic so you can
                # hard-kill connections and see them fail fast
                connection.session.publish('foo')

    print("exiting main")


if False:
    # "normal" usage
    runner = ApplicationRunner([dict(url="ws://127.0.0.1:8081/ws")], u"realm1")
    runner.run(ClientSession)
    print("exiting.")

else:
    # "Twisted native" and other "lower-level" usage
    react(main)
    print("exiting.")
