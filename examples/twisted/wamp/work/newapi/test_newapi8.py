from autobahn.twisted.wamp import Connection
from twisted.internet.defer import inlineCallbacks as coroutine
from twisted.internet.task import react

# A single session joins a first realm, leaves and joins another realm
# all over the same, still running transport


@coroutine
def main(transport):
    session = ApplicationSession()

    # join a first realm and do something
    yield session.join(transport, "myrealm1")
    result = yield session.call("com.myapp.add2", 2, 3)
    print("Result: {}".format(result))

    # leave the realm. the transport will NOT be closed!
    yield session.leave()

    # join a different realm and do something
    yield session.join(transport, "myrealm2")
    result = yield session.call("com.foobar.mul2", 2, 3)
    print("Result: {}".format(result))

    # leave the realm. the transport will NOT be closed!
    yield session.leave()

    # now close the transport. after this, the transport cannot
    # be reused!
    yield transport.close()


if __name__ == "__main__":
    connection = Connection(main)
    react(connection.start)
