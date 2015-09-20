from __future__ import print_function
from autobahn.twisted.wamp import Connection

def on_join(session):
    """
    This is user code triggered when a session was created on top of
    a connection, and the sessin has joined a realm.
    """
    print('session connected: {}'.format(session))

    def on_leave(details):
        print("on_leave", details)

    session.on.leave(on_leave)

    # explicitly leaving a realm will disconnect the connection
    # cleanly and not try to reconnect, but exit cleanly.
    return session.leave()


def on_create(session):
    print("on_create", session)
    session.on('join', on_join)


def run(on_create):
    """
    This could be a high level "runner" tool we ship.
    """
    from twisted.internet import reactor

    # multiple, configurable transports, either via dict-like config, or
    # from native Twisted endpoints
    transports = [
        {
            "type": "websocket",
            "url": u"ws://127.0.0.1:8080/ws"
        }
    ]

    # a connection connects and automatically reconnects WAMP client
    # transports to a WAMP router. A connection has a listener system
    # where user code can hook into different events : on_join
    connection = Connection(transports, main=on_create, realm=u'realm1',
                            loop=reactor)

    # the following returns a deferred that fires when the connection is
    # finally done: either by explicit close by user code, or by error or
    # when stop reconnecting
    done = connection.open()

    def failed(fail):
        print("Error:", fail.value)
        reactor.stop()
    done.addCallbacks(lambda _: reactor.stop(), failed)

    reactor.run()


if __name__ == '__main__':
    # here, run() could be s.th. we ship, and a user would just
    # provide a on_create() thing and run:
    run(on_create)
