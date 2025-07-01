import txaio

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def setup_alice(session, details):
    print("alice created", session)

    def on_join(session, details):
        print("alice joined", session, details)

    session.on("join", on_join)
    yield sleep(2)
    print("alice done sleeping")
    print("since we're a 'main' function we have to leave explicitly", session)
    print("Doing that in 2 seconds...")
    reactor.callLater(2, session.leave)


@inlineCallbacks
def setup_bob(reactor, session):
    print("bob created", session)

    def on_join(session, details):
        print("bob joined", session, details)

    session.on("join", on_join)
    yield sleep(1)
    print("bob done sleeping")


#    session.leave()


if __name__ == "__main__":
    transports = [{"type": "websocket", "url": "ws://127.0.0.1:8080/ws"}]

    component1 = Component(
        on_join=setup_alice, transports=transports, realm="crossbardemo"
    )
    component2 = Component(main=setup_bob, transports=transports, realm="crossbardemo")
    # run([component1, component2], log_level='debug')
    # run([component1, component2], log_level='info')
    run([component1], log_level="info")
    # run([component2], log_level='info')
