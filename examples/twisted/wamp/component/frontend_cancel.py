from autobahn.twisted.component import Component, run
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import RegisterOptions
from twisted.internet.defer import CancelledError, inlineCallbacks


@inlineCallbacks
def main(reactor, session):
    print("Client session={}".format(session))
    d = session.call("example.foo", "some", "args")
    print("Called 'example.foo': {}".format(d))
    print("cancel()-ing the above Deferred")

    d.cancel()

    try:
        res = yield d
        print("somehow we got a result: {}".format(res))
    except CancelledError:
        print("call was canceled successfully")
    print("done")


component = Component(
    transports="ws://localhost:8080/auth_ws",
    main=main,
    realm="crossbardemo",
)


if __name__ == "__main__":
    run([component])  # , log_level='debug')
