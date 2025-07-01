from autobahn.twisted.wamp import Connection
from twisted.internet.defer import inlineCallbacks as coroutine
from twisted.internet.task import react


@coroutine
def main(transport):
    session = yield transport.join("myrealm1")
    result = yield session.call("com.myapp.add2", 2, 3)
    print("Result: {}".format(result))
    yield session.leave()
    yield transport.close()


if __name__ == "__main__":
    connection = Connection(main)
    react(connection.start)
