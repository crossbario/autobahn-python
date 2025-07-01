from autobahn.twisted.connection import Connection
from twisted.internet.defer import inlineCallbacks as coroutine
from twisted.internet.task import react


@coroutine
def main(reactor, connection):
    transport = yield connection.connect()
    session = yield transport.join("realm1")
    result = yield session.call("com.example.add2", 2, 3)
    yield session.leave()
    yield transport.disconnect()
    yield connection.close()


if __name__ == "__main__":
    connection = Connection()
    connection.on("start", main)

    react(connection.start)
